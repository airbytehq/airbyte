package io.dataline.config.persistence;

import java.util.UUID;

public class PersistenceConstants {
  public static String DEFAULT_TEST_ROOT = "/tmp/data/config/";

  // for MVP we only support one workspace per deployment and we hard code its id.
  public static UUID DEFAULT_WORKSPACE_ID = UUID.fromString("5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6");
}
