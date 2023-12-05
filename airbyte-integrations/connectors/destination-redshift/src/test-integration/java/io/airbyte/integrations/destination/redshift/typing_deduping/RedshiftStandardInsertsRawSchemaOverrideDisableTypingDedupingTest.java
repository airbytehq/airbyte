/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertAll;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import io.airbyte.workers.internal.AirbyteDestination;
import java.util.List;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class RedshiftStandardInsertsRawSchemaOverrideDisableTypingDedupingTest extends AbstractRedshiftTypingDedupingTest {

  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_config_raw_schema_override.json";
  }

  @Override
  protected String getRawSchema() {
    return "overridden_raw_dataset";
  }

  @Override
  protected boolean disableFinalTableComparison() {
    return true;
  }

  @Disabled
  @Test
  @Override
  public void identicalNameSimultaneousSync() {}

}
