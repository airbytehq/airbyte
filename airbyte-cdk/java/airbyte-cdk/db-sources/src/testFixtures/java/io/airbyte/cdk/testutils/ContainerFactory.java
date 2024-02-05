/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.testutils;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.containers.output.Slf4jLogConsumer;
import org.testcontainers.utility.DockerImageName;

/**
 * ContainerFactory is the companion interface to {@link TestDatabase} for providing it with
 * suitable testcontainer instances.
 */
public interface ContainerFactory<C extends JdbcDatabaseContainer<?>> {

  /**
   * Creates a new, unshared testcontainer instance. This usually wraps the default constructor for
   * the testcontainer type.
   */
  C createNewContainer(DockerImageName imageName);

  /**
   * Returns the class object of the testcontainer.
   */
  Class<?> getContainerClass();

  /**
   * Returns a shared instance of the testcontainer.
   */
  default C shared(String imageName, String... methods) {
    final String mapKey = Stream.concat(
        Stream.of(imageName, this.getClass().getCanonicalName()),
        Stream.of(methods))
        .collect(Collectors.joining("+"));
    return Wrapper.getOrCreateShared(mapKey, this);
  }

  default C unshared(String imageName, String... methods) {
    return new Wrapper<C>(imageName, List.of(methods)).getOrCreate(this);
  }

   /**
   * This class can be used to wrap a specific shared testcontainer instance.
   */
  class Wrapper<C extends JdbcDatabaseContainer<?>> {

    static private final Logger LOGGER = LoggerFactory.getLogger(Wrapper.class);
    static private final ConcurrentHashMap<String, Wrapper<?>> SHARED = new ConcurrentHashMap<>();

    @SuppressWarnings("unchecked")
    static private <C extends JdbcDatabaseContainer<?>> C getOrCreateShared(String mapKey, ContainerFactory<C> factory) {
      final Wrapper<?> sharedContainerWrapper = SHARED.computeIfAbsent(mapKey, Wrapper<C>::new);
      return ((Wrapper<C>) sharedContainerWrapper).getOrCreate(factory);
    }

    final private String imageName;
    final private List<String> methodNames;

    private C container;
    private RuntimeException containerCreationError;

    private Wrapper(String imageNamePlusMethods) {
      final String[] parts = imageNamePlusMethods.split("\\+");
      this.imageName = parts[0];
      this.methodNames = Arrays.stream(parts).skip(2).toList();
    }

    private Wrapper(String imageName, List<String> methodNames) {
      this.imageName = imageName;
      this.methodNames = methodNames;
    }

    private synchronized C getOrCreate(ContainerFactory<C> factory) {
      if (container == null && containerCreationError == null) {
        try {
          create(imageName, factory, methodNames);
        } catch (RuntimeException e) {
          container = null;
          containerCreationError = e;
        }
      }
      if (containerCreationError != null) {
        throw new RuntimeException(
            "Error during container creation for imageName=" + imageName
                + ", factory=" + factory.getClass().getName()
                + ", methods=" + methodNames,
            containerCreationError);
      }
      return container;
    }

    private void create(String imageName, ContainerFactory<C> factory, List<String> methodNames) {
      LOGGER.info("Creating new container based on {} with {}.", imageName, methodNames);
      try {
        final var parsed = DockerImageName.parse(imageName);
        final var methods = new ArrayList<Method>();
        for (String methodName : methodNames) {
          methods.add(factory.getClass().getMethod(methodName, factory.getContainerClass()));
        }
        container = factory.createNewContainer(parsed);
        container.withLogConsumer(new Slf4jLogConsumer(LOGGER));
        for (Method method : methods) {
          LOGGER.info("Calling {} in {} on new container based on {}.",
              method.getName(), factory.getClass().getName(), imageName);
          method.invoke(factory, container);
        }
        container.start();
      } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
        throw new RuntimeException(e);
      }
    }

  }

}
