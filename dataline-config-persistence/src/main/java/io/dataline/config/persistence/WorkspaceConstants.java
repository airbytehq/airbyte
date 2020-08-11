package io.dataline.config.persistence;

import java.util.UUID;

public class WorkspaceConstants {
  // for MVP we only support one workspace per deployment and we hard code its id.
  public static UUID DEFAULT_WORKSPACE_ID = UUID.fromString("5e4991b7-b649-47e4-a65c-3bf4a0e7b65b");
}
