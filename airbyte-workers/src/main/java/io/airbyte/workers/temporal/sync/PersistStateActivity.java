/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.StandardSyncOutput;
import java.util.UUID;

public interface PersistStateActivity {

  boolean persist(final UUID connectionId, final StandardSyncOutput syncOutput);

}
