/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yugabytedb;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.utility.DockerImageName;

public class YugabytedbContainerInitializr {

  private static final Logger LOGGER = LoggerFactory.getLogger(YugabytedbContainerInitializr.class);

  private static YugabytedbContainer yugabytedbContainer;

  private YugabytedbContainerInitializr() {

  }

  public static YugabytedbContainer initContainer() {
    if (yugabytedbContainer == null) {
      yugabytedbContainer = new YugabytedbContainer();
    }
    yugabytedbContainer.start();
    return yugabytedbContainer;
  }

  static class YugabytedbContainer extends JdbcDatabaseContainer<YugabytedbContainer> {

    private static final int YUGABYTE_PORT = 5433;

    public YugabytedbContainer() {
      super(DockerImageName.parse("yugabytedb/yugabyte:2.15.2.0-b87"));

      this.setCommand("bin/yugabyted", "start", "--daemon=false");
      this.addExposedPort(YUGABYTE_PORT);

    }

    @Override
    public String getDriverClassName() {
      return "com.yugabyte.Driver";
    }

    @Override
    public String getJdbcUrl() {
      String params = constructUrlParameters("?", "&");
      return "jdbc:yugabytedb://" + getHost() + ":" + getMappedPort(YUGABYTE_PORT) + "/yugabyte" + params;
    }

    @Override
    public String getDatabaseName() {
      return "yugabyte";
    }

    @Override
    public String getUsername() {
      return "yugabyte";
    }

    @Override
    public String getPassword() {
      return "yugabyte";
    }

    @Override
    protected String getTestQueryString() {
      return "SELECT 1";
    }

  }

}
