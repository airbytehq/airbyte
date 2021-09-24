/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_factory;

import java.util.UUID;

public interface SyncJobFactory {

  Long create(UUID connectionId);

}
