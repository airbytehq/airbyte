/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.cdk.testutils.ContainerFactory;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.utility.DockerImageName;

public class MsSQLContainerFactory implements ContainerFactory<MSSQLServerContainer<?>> {

  @Override
  public MSSQLServerContainer<?> createNewContainer(DockerImageName imageName) {
    MSSQLServerContainer container =
        new MSSQLServerContainer<>(imageName.asCompatibleSubstituteFor("mcr.microsoft.com/mssql/server")).acceptLicense();
    container.addEnv("MSSQL_MEMORY_LIMIT_MB", "384");
    return container;
  }

  @Override
  public Class<?> getContainerClass() {
    return MSSQLServerContainer.class;
  }

  /**
   * Create a new network and bind it to the container.
   */
  public void withNetwork(MSSQLServerContainer<?> container) {
    container.withNetwork(Network.newNetwork());
  }

  public void withAgent(MSSQLServerContainer<?> container) {
    container.addEnv("MSSQL_AGENT_ENABLED", "True");
  }

}
