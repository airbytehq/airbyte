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
public interface ResetActivity {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class ResetInput {

    private UUID connectionId;

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class GetResetsOutput {

    private List<StreamDescriptor> streamDescriptorList;

  }

  /**
   * Return the streams being reset for a given connection id
   */
  @ActivityMethod
  GetResetsOutput getStreamResets(UUID connectionId);

  /**
   * Creates a stream_reset record for each stream descriptor passed in
   */
  @ActivityMethod
  void createStreamResets(UUID connectionId, List<StreamDescriptor> streamDescriptorList);

  /**
   * Deletes the stream_reset record corresponding to each stream descriptor passed in
   */
  @ActivityMethod
  void deleteStreamResets(UUID connectionId, List<StreamDescriptor> streamDescriptorList);

}
