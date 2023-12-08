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
    return Singleton.getOrCreate(mapKey, this);
  }

  /**
   * This class is exclusively used by {@link #shared(String, String...)}. It wraps a specific shared
   * testcontainer instance, which is created exactly once.
   */
  class Singleton<C extends JdbcDatabaseContainer<?>> {

    static private final Logger LOGGER = LoggerFactory.getLogger(Singleton.class);
    static private final ConcurrentHashMap<String, Singleton<?>> LAZY = new ConcurrentHashMap<>();

    @SuppressWarnings("unchecked")
    static private <C extends JdbcDatabaseContainer<?>> C getOrCreate(String mapKey, ContainerFactory<C> factory) {
      final Singleton<?> singleton = LAZY.computeIfAbsent(mapKey, Singleton<C>::new);
      return ((Singleton<C>) singleton).getOrCreate(factory);
    }

    final private String imageName;
    final private List<String> methodNames;

    private C sharedContainer;
    private RuntimeException containerCreationError;

    private Singleton(String imageNamePlusMethods) {
      final String[] parts = imageNamePlusMethods.split("\\+");
      this.imageName = parts[0];
      this.methodNames = Arrays.stream(parts).skip(2).toList();
    }

    private synchronized C getOrCreate(ContainerFactory<C> factory) {
      if (sharedContainer == null && containerCreationError == null) {
        try {
          create(imageName, factory, methodNames);
        } catch (RuntimeException e) {
          sharedContainer = null;
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
      return sharedContainer;
    }

    private void create(String imageName, ContainerFactory<C> factory, List<String> methodNames) {
      LOGGER.info("Creating new shared container based on {} with {}.", imageName, methodNames);
      try {
        final var parsed = DockerImageName.parse(imageName);
        final var methods = new ArrayList<Method>();
        for (String methodName : methodNames) {
          methods.add(factory.getClass().getMethod(methodName, factory.getContainerClass()));
        }
        sharedContainer = factory.createNewContainer(parsed);
        sharedContainer.withLogConsumer(new Slf4jLogConsumer(LOGGER));
        for (Method method : methods) {
          LOGGER.info("Calling {} in {} on new shared container based on {}.",
              method.getName(), factory.getClass().getName(), imageName);
          method.invoke(factory, sharedContainer);
        }
        sharedContainer.start();
      } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
        throw new RuntimeException(e);
      }
    }

  }

}
