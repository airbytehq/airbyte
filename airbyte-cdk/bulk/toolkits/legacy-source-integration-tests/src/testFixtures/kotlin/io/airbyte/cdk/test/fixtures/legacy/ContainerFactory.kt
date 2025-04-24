/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import io.github.oshai.kotlinlogging.DelegatingKLogger
import io.github.oshai.kotlinlogging.KLogger
import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.reflect.InvocationTargetException
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.atomic.AtomicInteger
import java.util.function.Consumer
import java.util.function.Supplier
import kotlin.concurrent.Volatile
import org.slf4j.Logger
import org.testcontainers.containers.GenericContainer
import org.testcontainers.containers.output.OutputFrame
import org.testcontainers.containers.output.Slf4jLogConsumer
import org.testcontainers.utility.DockerImageName

private val LOGGER: KLogger = KotlinLogging.logger {}
/**
 * ContainerFactory is the companion to [TestDatabase] and provides it with suitable testcontainer
 * instances.
 */
abstract class ContainerFactory<C : GenericContainer<*>> {
    @JvmRecord
    private data class ContainerKey<C : GenericContainer<*>>(
        val clazz: Class<out ContainerFactory<*>>,
        val imageName: DockerImageName,
        val methods: List<String>
    )

    private class ContainerOrException(
        private val containerSupplier: Supplier<GenericContainer<*>>
    ) {
        @Volatile private lateinit var _exception: RuntimeException

        @Volatile private lateinit var _container: GenericContainer<*>

        fun container(): GenericContainer<*> {
            if (!::_exception.isInitialized && !::_container.isInitialized) {
                synchronized(this) {
                    if (!::_exception.isInitialized && !::_container.isInitialized) {
                        try {
                            _container = containerSupplier.get()
                            checkNotNull(_container) {
                                "testcontainer instance was not constructed"
                            }
                        } catch (e: RuntimeException) {
                            _exception = e
                        }
                    }
                }
            }
            if (::_exception.isInitialized) {
                throw _exception
            }
            return _container
        }
    }

    private fun getTestContainerLogMdcBuilder(
        imageName: DockerImageName,
        containerModifiers: List<Pair<Consumer<C>, String>>
    ): MdcScope.Builder {
        return MdcScope.Builder()
            .setLogPrefix(
                "testcontainer ${containerId.incrementAndGet()} ($imageName[${containerModifiers.joinToString(",") { it.second }}]):"
            )
            .setPrefixColor(LoggingHelper.Color.RED_BACKGROUND)
    }

    /**
     * Creates a new, unshared testcontainer instance. This usually wraps the default constructor
     * for the testcontainer type.
     */
    protected abstract fun createNewContainer(imageName: DockerImageName): C

    /**
     * Returns a shared instance of the testcontainer.
     *
     * @Deprecated use shared(String, NamedContainerModifier) instead
     */
    fun shared(imageName: String, vararg methods: String): C {
        return shared(imageName, methods.map { resolveModifierByName(it) to it })
    }

    fun <N> shared(imageName: String, vararg namedContainerModifiers: N): C where
    N : NamedContainerModifier<C>,
    N : Enum<N> {
        return shared(imageName, listOf(*namedContainerModifiers).map { it.modifier to it.name })
    }

    @JvmOverloads
    fun shared(
        imageName: String,
        containerModifiersWithNames: List<Pair<Consumer<C>, String>> = ArrayList()
    ): C {
        val containerKey =
            ContainerKey<C>(
                javaClass,
                DockerImageName.parse(imageName),
                containerModifiersWithNames.map { it.second }
            )
        // We deliberately avoid creating the container itself eagerly during the evaluation of the
        // map
        // value.
        // Container creation can be exceedingly slow.
        // Furthermore, we need to handle exceptions raised during container creation.
        val containerOrError =
            SHARED_CONTAINERS.computeIfAbsent(containerKey) { key: ContainerKey<*> ->
                ContainerOrException {
                    createAndStartContainer(key.imageName, containerModifiersWithNames)
                }
            }
        // Instead, the container creation (if applicable) is deferred to here.
        @Suppress("UNCHECKED_CAST") return containerOrError!!.container() as C
    }

    /**
     * Returns an exclusive instance of the testcontainer.
     *
     * @Deprecated use exclusive(String, NamedContainerModifier) instead
     */
    fun exclusive(imageName: String, vararg methods: String): C {
        return exclusiveInternal(imageName, methods.map { resolveModifierByName(it) to it })
    }

    fun <N> exclusive(imageName: String, vararg namedContainerModifiers: N): C where
    N : NamedContainerModifier<C>,
    N : Enum<N> {
        return exclusive(imageName, listOf(*namedContainerModifiers))
    }

    @JvmOverloads
    fun <N> exclusive(imageName: String, namedContainerModifiers: List<N> = ArrayList()): C where
    N : NamedContainerModifier<C>,
    N : Enum<N> {
        return exclusiveInternal(imageName, namedContainerModifiers.map { it.modifier to it.name })
    }

    // Yeah, this is a bad name. We need something different because of type erasure :(
    fun exclusiveInternal(
        imageName: String,
        containerModifiersWithNames: List<Pair<Consumer<C>, String>>
    ): C {
        return createAndStartContainer(
            DockerImageName.parse(imageName),
            containerModifiersWithNames
        )
    }

    interface NamedContainerModifier<C : GenericContainer<*>> {
        val modifier: Consumer<C>
    }

    class NamedContainerModifierImpl<C : GenericContainer<*>>(
        val name: String,
        override val modifier: Consumer<C>
    ) : NamedContainerModifier<C> {}

    private fun resolveModifierByName(methodName: String): Consumer<C> {
        val self: ContainerFactory<C> = this
        val resolvedMethod = Consumer { c: C ->
            try {
                val containerClass: Class<out GenericContainer<*>> = c.javaClass
                val method = self.javaClass.getMethod(methodName, containerClass)
                method.invoke(self, c)
            } catch (e: NoSuchMethodException) {
                throw RuntimeException(e)
            } catch (e: IllegalAccessException) {
                throw RuntimeException(e)
            } catch (e: InvocationTargetException) {
                throw RuntimeException(e)
            }
        }
        return resolvedMethod
    }

    private fun createAndStartContainer(
        imageName: DockerImageName,
        containerModifiersWithNames: List<Pair<Consumer<C>, String>>
    ): C {
        LOGGER.info(
            "Creating new container based on {} with {}.",
            imageName,
            containerModifiersWithNames.map { it.second }
        )
        val container = createNewContainer(imageName)
        @Suppress("unchecked_cast")
        val logConsumer: Slf4jLogConsumer =
            object : Slf4jLogConsumer((LOGGER as DelegatingKLogger<Logger>).underlyingLogger) {
                override fun accept(frame: OutputFrame) {
                    if (frame.utf8StringWithoutLineEnding.trim { it <= ' ' }.isNotEmpty()) {
                        super.accept(frame)
                    }
                }
            }
        getTestContainerLogMdcBuilder(imageName, containerModifiersWithNames).produceMappings {
            key: String?,
            value: String ->
            logConsumer.withMdc(key, value)
        }
        container.withLogConsumer(logConsumer)
        for (resolvedNamedContainerModifier in containerModifiersWithNames) {
            LOGGER.info(
                "Calling {} in {} on new container based on {}.",
                resolvedNamedContainerModifier.second,
                javaClass.name,
                imageName
            )
            resolvedNamedContainerModifier.first.accept(container)
        }
        container.start()
        return container
    }

    companion object {
        private val SHARED_CONTAINERS: ConcurrentMap<ContainerKey<*>, ContainerOrException> =
            ConcurrentHashMap()
        private val containerId: AtomicInteger = AtomicInteger(0)
    }
}
