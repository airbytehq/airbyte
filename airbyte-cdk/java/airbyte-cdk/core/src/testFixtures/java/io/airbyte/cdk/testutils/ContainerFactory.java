/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.testutils;

import com.google.common.collect.Lists;
import io.airbyte.commons.logging.LoggingHelper;
import io.airbyte.commons.logging.MdcScope;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import java.util.function.Supplier;
import java.util.stream.Stream;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.output.OutputFrame;
import org.testcontainers.containers.output.Slf4jLogConsumer;
import org.testcontainers.utility.DockerImageName;

/**
 * ContainerFactory is the companion to {@link TestDatabase} and provides it with suitable
 * testcontainer instances.
 */
public abstract class ContainerFactory<C extends GenericContainer<?>> {

  static private final Logger LOGGER = LoggerFactory.getLogger(ContainerFactory.class);

  private record ContainerKey<C extends GenericContainer<?>> (Class<? extends ContainerFactory> clazz,
                                                              DockerImageName imageName,
                                                              List<? extends NamedContainerModifier<C>> methods) {}

  ;

  private static class ContainerOrException {

    private final Supplier<GenericContainer<?>> containerSupplier;
    private volatile RuntimeException _exception = null;
    private volatile GenericContainer<?> _container = null;

    ContainerOrException(Supplier<GenericContainer<?>> containerSupplier) {
      this.containerSupplier = containerSupplier;
    }

    GenericContainer<?> container() {
      if (_exception == null && _container == null) {
        synchronized (this) {
          if (_container == null && _exception == null) {
            try {
              _container = containerSupplier.get();
              if (_container == null) {
                throw new IllegalStateException("testcontainer instance was not constructed");
              }
            } catch (RuntimeException e) {
              _exception = e;
            }
          }
        }
      }
      if (_exception != null) {
        throw _exception;
      }
      return _container;
    }

  }

  private static final ConcurrentMap<ContainerKey<?>, ContainerOrException> SHARED_CONTAINERS = new ConcurrentHashMap<>();
  private static final AtomicInteger containerId = new AtomicInteger(0);

  private final MdcScope.Builder getTestContainerLogMdcBuilder(DockerImageName imageName,
                                                               List<? extends NamedContainerModifier<C>> containerModifiers) {
    return new MdcScope.Builder()
        .setLogPrefix("testcontainer %s (%s[%s]):".formatted(containerId.incrementAndGet(), imageName, StringUtils.join(containerModifiers, ",")))
        .setPrefixColor(LoggingHelper.Color.RED_BACKGROUND);
  }

  /**
   * Creates a new, unshared testcontainer instance. This usually wraps the default constructor for
   * the testcontainer type.
   */
  protected abstract C createNewContainer(DockerImageName imageName);

  /**
   * Returns a shared instance of the testcontainer.
   *
   * @Deprecated use shared(String, NamedContainerModifier) instead
   */
  @Deprecated
  public final C shared(String imageName, String... methods) {
    return shared(imageName,
        Stream.of(methods).map(n -> new NamedContainerModifierImpl<C>(n, resolveModifierByName(n))).toList());
  }

  public final C shared(String imageName, NamedContainerModifier<C>... namedContainerModifiers) {
    return shared(imageName, List.of(namedContainerModifiers));
  }

  public final C shared(String imageName) {
    return shared(imageName, new ArrayList<>());
  }

  public final C shared(String imageName, List<? extends NamedContainerModifier<C>> namedContainerModifiers) {
    final ContainerKey<C> containerKey = new ContainerKey<>(getClass(), DockerImageName.parse(imageName), namedContainerModifiers);
    // We deliberately avoid creating the container itself eagerly during the evaluation of the map
    // value.
    // Container creation can be exceedingly slow.
    // Furthermore, we need to handle exceptions raised during container creation.
    ContainerOrException containerOrError = SHARED_CONTAINERS.computeIfAbsent(containerKey,
        key -> new ContainerOrException(() -> createAndStartContainer(key.imageName(), ((ContainerKey<C>) key).methods())));
    // Instead, the container creation (if applicable) is deferred to here.
    return (C) containerOrError.container();
  }

  /**
   * Returns an exclusive instance of the testcontainer.
   *
   * @Deprecated use exclusive(String, NamedContainerModifier) instead
   */
  @SuppressWarnings("unchecked")
  @Deprecated
  public final C exclusive(String imageName, String... methods) {
    return exclusive(imageName, Stream.of(methods).map(n -> new NamedContainerModifierImpl<C>(n, resolveModifierByName(n))).toList());
  }

  public final C exclusive(String imageName) {
    return exclusive(imageName, new ArrayList<>());
  }

  public final C exclusive(String imageName, NamedContainerModifier<C>... namedContainerModifiers) {
    return exclusive(imageName, List.of(namedContainerModifiers));
  }

  public final C exclusive(String imageName, List<? extends NamedContainerModifier<C>> namedContainerModifiers) {
    return (C) createAndStartContainer(DockerImageName.parse(imageName), namedContainerModifiers);
  }

  public interface NamedContainerModifier<C extends GenericContainer<?>> {

    String name();

    Consumer<C> modifier();

  }

  public record NamedContainerModifierImpl<C extends GenericContainer<?>> (String name, Consumer<C> method) implements NamedContainerModifier<C> {

    public String name() {
      return name;
    }

    public Consumer<C> modifier() {
      return method;
    }

  }

  private Consumer<C> resolveModifierByName(String methodName) {
    final ContainerFactory<C> self = this;
    Consumer<C> resolvedMethod = c -> {
      try {
        Class<? extends GenericContainer> containerClass = c.getClass();
        Method method = self.getClass().getMethod(methodName, containerClass);
        method.invoke(self, c);
      } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
        throw new RuntimeException(e);
      }
    };
    return resolvedMethod;
  }

  private C createAndStartContainer(DockerImageName imageName, List<? extends NamedContainerModifier<C>> namedContainerModifiers) {
    LOGGER.info("Creating new container based on {} with {}.", imageName, Lists.transform(namedContainerModifiers, c -> c.name()));
    C container = createNewContainer(imageName);
    final var logConsumer = new Slf4jLogConsumer(LOGGER) {

      public void accept(OutputFrame frame) {
        if (frame.getUtf8StringWithoutLineEnding().trim().length() > 0) {
          super.accept(frame);
        }
      }

    };
    getTestContainerLogMdcBuilder(imageName, namedContainerModifiers).produceMappings(logConsumer::withMdc);
    container.withLogConsumer(logConsumer);
    for (NamedContainerModifier<C> resolvedNamedContainerModifier : namedContainerModifiers) {
      LOGGER.info("Calling {} in {} on new container based on {}.",
          resolvedNamedContainerModifier.name(), getClass().getName(), imageName);
      resolvedNamedContainerModifier.modifier().accept(container);
    }
    container.start();
    return container;
  }

}
