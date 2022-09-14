/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.workers.temporal.TemporalJobType;
import io.micronaut.context.annotation.Value;
import io.micronaut.core.util.StringUtils;
import java.util.Arrays;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import javax.inject.Singleton;

@Singleton
public class RouterService {

  static final String MVP_DATA_PLANE_TASK_QUEUE = "MVP_DATA_PLANE";

  @Value("${airbyte.data.plane.connection-ids-mvp}")
  private String connectionIdsForMvpDataPlane;

  /**
   * For now, returns a Task Queue by checking to see if the connectionId is on the env var list for
   * usage in the MVP Data Plane. This will be replaced by a proper Router Service in the future.
   */
  public String getTaskQueue(final UUID connectionId) {
    if (connectionId != null) {
      if (getConnectionIdsForMvpDataPlane().contains(connectionId.toString())) {
        return MVP_DATA_PLANE_TASK_QUEUE;
      }
    }
    return TemporalJobType.SYNC.name();
  }

  private Set<String> getConnectionIdsForMvpDataPlane() {
    return StringUtils.isNotEmpty(connectionIdsForMvpDataPlane) ? Arrays.stream(connectionIdsForMvpDataPlane.split(",")).collect(Collectors.toSet())
        : Set.of();
  }

  @VisibleForTesting
  void setConnectionIdsForMvpDataPlane(final String connectionIdsForMvpDataPlane) {
    this.connectionIdsForMvpDataPlane = connectionIdsForMvpDataPlane;
  }

}
