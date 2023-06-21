/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyStagingStorageType.S3;

import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.copy.SwitchingDestination;
import java.io.Closeable;
import java.sql.DriverManager;

public class StarburstGalaxyDestination extends SwitchingDestination<StarburstGalaxyStagingStorageType> {

  public StarburstGalaxyDestination() {
    super(StarburstGalaxyStagingStorageType.class,
        StarburstGalaxyDestinationResolver::getStagingStorageType,
        ImmutableMap.of(S3, new StarburstGalaxyS3Destination()));
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new StarburstGalaxyDestination();
    new IntegrationRunner(destination).run(args);
    ((Closeable) DriverManager.getDriver("jdbc:trino:")).close();
  }

}
