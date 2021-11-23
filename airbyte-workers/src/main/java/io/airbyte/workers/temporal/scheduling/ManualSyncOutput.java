/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import lombok.Value;

@Value
public class ManualSyncOutput {

  private final boolean submitted;

}
