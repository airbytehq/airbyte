/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.StreamDescriptor;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.util.List;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface StreamResetActivity {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class GetResetsOutput {

    private List<StreamDescriptor> streamDescriptorList;

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class DeleteStreamResetsInput {

    private UUID connectionId;
    private List<StreamDescriptor> streamDescriptorList;

  }

  /**
   * Deletes the stream_reset record corresponding to each stream descriptor passed in
   */
  @ActivityMethod
  void deleteStreamResets(DeleteStreamResetsInput streamsToDelete);

}
