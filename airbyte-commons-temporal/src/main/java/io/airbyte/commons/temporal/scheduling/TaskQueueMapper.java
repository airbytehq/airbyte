/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import io.airbyte.config.Geography;

/**
 * Maps a {@link Geography} to a Temporal Task Queue that should be used to run syncs for the given
 * Geography.
 */
public interface TaskQueueMapper {

  String getTaskQueue(Geography geography);

}
