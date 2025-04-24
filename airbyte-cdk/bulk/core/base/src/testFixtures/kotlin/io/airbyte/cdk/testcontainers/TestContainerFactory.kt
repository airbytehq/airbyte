/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.testcontainers

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.atomic.AtomicInteger
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.testcontainers.containers.GenericContainer
import org.testcontainers.containers.output.OutputFrame
import org.testcontainers.containers.output.Slf4jLogConsumer
import org.testcontainers.utility.DockerImageName

/** ContainerFactory provides us with suitably provisioned testcontainers. */
object TestContainerFactory {
    private val logger: Logger = LoggerFactory.getLogger(TestContainerFactory::class.java)
    private val specificFactories: ConcurrentMap<DockerImageName, SpecificTestContainerFactory<*>> =
        ConcurrentHashMap()
    private val sharedContainers: ConcurrentMap<ContainerKey, () -> Result<GenericContainer<*>>> =
        ConcurrentHashMap()
    private val counter = AtomicInteger()

    class SpecificTestContainerFactory<C : GenericContainer<*>>(
        val defaultImageName: DockerImageName,
        val constructor: (DockerImageName) -> C,
    ) {
        @Suppress("UNCHECKED_CAST")
        fun createAndStart(
            imageName: DockerImageName,
            vararg modifiers: ContainerModifier<C>,
        ): C {
            val modifierNames: String = modifiers.map { it.name }.joinToString(" ")
            logger.info("Creating new container based on {} with {}.", imageName, modifierNames)
            val container: GenericContainer<*> = constructor(imageName)
            container.withLogConsumer(
                object : Slf4jLogConsumer(logger) {
                    override fun accept(frame: OutputFrame) {
                        if (!frame.utf8StringWithoutLineEnding.isNullOrBlank()) {
                            super.accept(frame)
                        }
                    }
                },
            )
            val id: Int = counter.incrementAndGet()
            val logPrefix = "testcontainer #$id $imageName with $modifierNames"
            LoggingHelper.logPrefixMdc(logPrefix, LoggingHelper.Color.RED_BACKGROUND)
            for (modifier in modifiers) {
                logger.info(
                    "Calling {} in {} on new container based on {}.",
                    modifier.name,
                    javaClass.name,
                    imageName,
                )
                modifier.modify(container as C)
            }
            container.start()
            return container as C
        }
    }

    interface ContainerModifier<C : GenericContainer<*>> {
        val name: String
            get() = toString()

        fun modify(container: C)
    }

    private fun findFactory(dockerImageName: DockerImageName): SpecificTestContainerFactory<*> {
        specificFactories.forEach { (_, factory: SpecificTestContainerFactory<*>) ->
            if (
                dockerImageName == factory.defaultImageName ||
                    dockerImageName.isCompatibleWith(factory.defaultImageName)
            ) {
                return factory
            }
        }
        throw NoSuchElementException("no factory registered for $dockerImageName")
    }

    private data class ContainerKey(
        val factoryKey: DockerImageName,
        val imageName: DockerImageName,
        val modifierNames: List<String>,
    )

    /** Registers the constructor for testcontainers of type [C]. */
    fun <C : GenericContainer<*>> register(
        testContainerImageName: String,
        constructor: (DockerImageName) -> C,
    ) {
        register(DockerImageName.parse(testContainerImageName), constructor)
    }

    /** Registers the constructor for testcontainers of type [C]. */
    fun <C : GenericContainer<*>> register(
        testContainerImageName: DockerImageName,
        constructor: (DockerImageName) -> C,
    ) {
        val specificFactory = SpecificTestContainerFactory(testContainerImageName, constructor)
        specificFactories[testContainerImageName] = specificFactory
    }

    fun <C : GenericContainer<*>> newModifier(
        name: String,
        fn: (C) -> Unit,
    ): ContainerModifier<C> =
        object : ContainerModifier<C> {
            override val name: String = name

            override fun modify(container: C) {
                fn(container)
            }

            override fun toString(): String = name
        }

    /** Returns an exclusive instance of the testcontainer. */
    @Suppress("UNCHECKED_CAST")
    fun <C : GenericContainer<*>> exclusive(
        dockerImageName: DockerImageName,
        vararg containerModifiers: ContainerModifier<C>,
    ): C {
        val factory: SpecificTestContainerFactory<C> =
            findFactory(dockerImageName) as SpecificTestContainerFactory<C>
        return factory.createAndStart(dockerImageName, *containerModifiers)
    }

    /** Returns a shared instance of the testcontainer. */
    @Suppress("UNCHECKED_CAST")
    fun <C : GenericContainer<*>> shared(
        dockerImageName: DockerImageName,
        vararg containerModifiers: ContainerModifier<C>,
    ): C {
        val factory: SpecificTestContainerFactory<C> =
            findFactory(dockerImageName) as SpecificTestContainerFactory<C>
        val containerKey =
            ContainerKey(
                factory.defaultImageName,
                dockerImageName,
                containerModifiers.map { it.name },
            )
        val newResult: Result<C> by lazy {
            factory.runCatching { createAndStart(dockerImageName, *containerModifiers) }
        }
        // We deliberately avoid creating the container itself eagerly during the evaluation of the
        // map value. Container creation can be exceedingly slow.
        // Furthermore, we need to handle exceptions raised during container creation.
        val supplier: () -> Result<C> =
            sharedContainers.computeIfAbsent(containerKey) { { newResult } } as () -> Result<C>
        // Instead, the container creation (if applicable) is deferred to here.
        return supplier().getOrThrow()
    }
}
