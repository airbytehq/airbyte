package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;

public class CtidFeatureFlags {
  public static final String CDC_VIA_CTID = "cdc_via_ctid";
  public static final String CURSOR_VIA_CTID = "cursor_via_ctid";
  private final JsonNode sourceConfig;
  public CtidFeatureFlags(final JsonNode sourceConfig) {
    this.sourceConfig = sourceConfig;
  }
  public boolean isCdcSyncEnabled() {
    return getFlagValue(CDC_VIA_CTID);
  }

  public boolean isCursorSyncEnabled() {
    return getFlagValue(CURSOR_VIA_CTID);
  }

  private boolean getFlagValue(final String flag) {
    return sourceConfig.has(flag) && sourceConfig.get(flag).asBoolean();
  }

}
