/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.testutils;

import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.testcontainers.containers.JdbcDatabaseContainer;
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
    return ContainerFactoryWrapper.getOrCreate(mapKey, this);
  }

}
