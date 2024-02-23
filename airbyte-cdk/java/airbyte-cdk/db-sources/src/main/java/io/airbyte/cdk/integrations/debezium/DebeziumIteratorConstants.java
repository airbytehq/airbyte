/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium;

import java.time.Duration;

public class DebeziumIteratorConstants {

  public static final String SYNC_CHECKPOINT_DURATION_PROPERTY = "sync_checkpoint_seconds";
  public static final String SYNC_CHECKPOINT_RECORDS_PROPERTY = "sync_checkpoint_records";

  public static final Duration SYNC_CHECKPOINT_DURATION = Duration.ofMinutes(15);
  public static final Integer SYNC_CHECKPOINT_RECORDS = 10_000;

}
