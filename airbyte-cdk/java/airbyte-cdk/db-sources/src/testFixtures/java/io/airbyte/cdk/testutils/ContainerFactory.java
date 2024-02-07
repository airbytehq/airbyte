/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.testutils;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.containers.output.Slf4jLogConsumer;
import org.testcontainers.utility.DockerImageName;

/**
 * ContainerFactory is the companion to {@link TestDatabase} and provides it with
 * suitable testcontainer instances.
 */
public abstract class ContainerFactory<C extends JdbcDatabaseContainer<?>> {

  static private final Logger LOGGER = LoggerFactory.getLogger(ContainerFactory.class);

  private record ContainerKey(Class<? extends ContainerFactory> clazz, DockerImageName imageName, List<String> methods) {};

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

  private static final ConcurrentMap<ContainerKey, ContainerOrException> SHARED_CONTAINERS = new ConcurrentHashMap<>();

  /**
   * Creates a new, unshared testcontainer instance. This usually wraps the default constructor for
   * the testcontainer type.
   */
  protected abstract C createNewContainer(DockerImageName imageName);

  /**
   * Returns a shared instance of the testcontainer.
   */
  @SuppressWarnings("unchecked")
  public final C shared(String imageName, String... methods) {
    List<String> methodList = methods == null ? Collections.emptyList() : Arrays.asList(methods);
    DockerImageName dockerImageName = DockerImageName.parse(imageName);
    final ContainerKey containerKey = new ContainerKey(getClass(), dockerImageName, methodList);
    // We deliberately avoid creating the container itself eagerly during the evaluation of the map value.
    // Container creation can be exceedingly slow.
    // Furthermore, we need to handle exceptions raised during container creation.
    ContainerOrException containerOrError = SHARED_CONTAINERS.computeIfAbsent(containerKey, key ->
      new ContainerOrException(() -> createAndStartContainer(key.imageName(), key.methods()))
    );
    // Instead, the container creation (if applicable) is deferred to here.
    return (C) containerOrError.container();
  }

  @SuppressWarnings("unchecked")
  public final C exclusive(String imageName, String... methods) {
    DockerImageName dockerImageName = DockerImageName.parse(imageName);
    List<String> methodList = methods == null ? Collections.emptyList() : Arrays.asList(methods);
    return (C) createAndStartContainer(dockerImageName, methodList);
  }

  private GenericContainer<?> createAndStartContainer(DockerImageName imageName, List<String> methodNames) {
    LOGGER.info("Creating new shared container based on {} with {}.", imageName, methodNames);
    try {
      GenericContainer<?> container = createNewContainer(imageName);
      final var methods = new ArrayList<Method>();
      for (String methodName : methodNames) {
        methods.add(getClass().getMethod(methodName, container.getClass()));
      }
      container.withLogConsumer(new Slf4jLogConsumer(LOGGER));
      for (Method method : methods) {
        LOGGER.info("Calling {} in {} on new shared container based on {}.",
            method.getName(), getClass().getName(), imageName);
        method.invoke(this, container);
      }
      container.start();
      return container;
    } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
      throw new RuntimeException(e);
    }
  }

}
