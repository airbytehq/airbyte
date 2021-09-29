/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import com.google.common.collect.ImmutableList;
import io.airbyte.migrate.migrations.MigrationV0_14_0;
import io.airbyte.migrate.migrations.MigrationV0_14_3;
import io.airbyte.migrate.migrations.MigrationV0_17_0;
import io.airbyte.migrate.migrations.MigrationV0_18_0;
import io.airbyte.migrate.migrations.MigrationV0_20_0;
import io.airbyte.migrate.migrations.MigrationV0_23_0;
import io.airbyte.migrate.migrations.MigrationV0_24_0;
import io.airbyte.migrate.migrations.MigrationV0_25_0;
import io.airbyte.migrate.migrations.MigrationV0_26_0;
import io.airbyte.migrate.migrations.MigrationV0_27_0;
import io.airbyte.migrate.migrations.MigrationV0_28_0;
import io.airbyte.migrate.migrations.MigrationV0_29_0;
import io.airbyte.migrate.migrations.NoOpMigration;
import java.util.List;

public class Migrations {

  private static final Migration MIGRATION_V_0_14_0 = new MigrationV0_14_0();
  private static final Migration MIGRATION_V_0_14_3 = new MigrationV0_14_3(MIGRATION_V_0_14_0);
  private static final Migration MIGRATION_V_0_15_0 = new NoOpMigration(MIGRATION_V_0_14_3, "0.15.0-alpha");
  private static final Migration MIGRATION_V_0_16_0 = new NoOpMigration(MIGRATION_V_0_15_0, "0.16.0-alpha");
  private static final Migration MIGRATION_V_0_17_0 = new MigrationV0_17_0(MIGRATION_V_0_16_0);
  private static final Migration MIGRATION_V_0_18_0 = new MigrationV0_18_0(MIGRATION_V_0_17_0);
  private static final Migration MIGRATION_V_0_19_0 = new NoOpMigration(MIGRATION_V_0_18_0, "0.19.0-alpha");
  private static final Migration MIGRATION_V_0_20_0 = new MigrationV0_20_0(MIGRATION_V_0_19_0);
  private static final Migration MIGRATION_V_0_21_0 = new NoOpMigration(MIGRATION_V_0_20_0, "0.21.0-alpha");
  private static final Migration MIGRATION_V_0_22_0 = new NoOpMigration(MIGRATION_V_0_21_0, "0.22.0-alpha");
  private static final Migration MIGRATION_V_0_23_0 = new MigrationV0_23_0(MIGRATION_V_0_22_0);
  private static final Migration MIGRATION_V_0_24_0 = new MigrationV0_24_0(MIGRATION_V_0_23_0);
  private static final Migration MIGRATION_V_0_25_0 = new MigrationV0_25_0(MIGRATION_V_0_24_0);
  private static final Migration MIGRATION_V_0_26_0 = new MigrationV0_26_0(MIGRATION_V_0_25_0);
  private static final Migration MIGRATION_V_0_27_0 = new MigrationV0_27_0(MIGRATION_V_0_26_0);
  public static final Migration MIGRATION_V_0_28_0 = new MigrationV0_28_0(MIGRATION_V_0_27_0);
  public static final Migration MIGRATION_V_0_29_0 = new MigrationV0_29_0(MIGRATION_V_0_28_0);
  public static final Migration MIGRATION_V_0_30_0 = new NoOpMigration(MIGRATION_V_0_29_0, "0.30.0-alpha");

  // all migrations must be added to the list in the order that they should be applied.
  public static final List<Migration> MIGRATIONS = ImmutableList.of(
      MIGRATION_V_0_14_0,
      MIGRATION_V_0_14_3,
      MIGRATION_V_0_15_0,
      MIGRATION_V_0_16_0,
      MIGRATION_V_0_17_0,
      MIGRATION_V_0_18_0,
      MIGRATION_V_0_19_0,
      MIGRATION_V_0_20_0,
      MIGRATION_V_0_21_0,
      MIGRATION_V_0_22_0,
      MIGRATION_V_0_23_0,
      MIGRATION_V_0_24_0,
      MIGRATION_V_0_25_0,
      MIGRATION_V_0_26_0,
      MIGRATION_V_0_27_0,
      MIGRATION_V_0_28_0,
      MIGRATION_V_0_29_0,
      MIGRATION_V_0_30_0);

}
