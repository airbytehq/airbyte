/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.testutils;

import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

/**
 * ContainerFactory is the companion interface to {@link TestDatabase} for providing it with
 * suitable testcontainer instances.
 */
public interface ContainerFactory<C extends GenericContainer<?>> {

  /**
   * Creates a new, unshared testcontainer instance. This usually wraps the default constructor for
   * the testcontainer type. Unless you know exactly what you're doing, call
   * {@link #shared(String, String...)} or {@link #exclusive(String, String...)} instead.
   */
  C createNewContainer(DockerImageName imageName);

  /**
   * Returns the class object of the testcontainer.
   */
  Class<?> getContainerClass();

  /**
   * Returns a shared instance of the testcontainer.
   */
  @SuppressWarnings("unchecked")
  default C shared(String imageName, String... methods) {
    return (C) ContainerFactoryWrapper.getOrCreateShared(this, imageName, methods);
  }

  /**
   * Returns a new, unshared instance of the testcontainer.
   */
  @SuppressWarnings("unchecked")
  default C exclusive(String imageName, String... methods) {
    return (C) ContainerFactoryWrapper.createExclusive(this, imageName, methods);
  }

}
