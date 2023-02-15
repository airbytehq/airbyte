/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.util.UUID;

@ActivityInterface
public interface NormalizationActivity {

  @ActivityMethod
  NormalizationSummary normalize(JobRunConfig jobRunConfig,
                                 IntegrationLauncherConfig destinationLauncherConfig,
                                 NormalizationInput input);

  @ActivityMethod
  NormalizationInput generateNormalizationInput(final StandardSyncInput syncInput, final StandardSyncOutput syncOutput);

  @ActivityMethod
  NormalizationInput generateNormalizationInputWithMinimumPayload(final JsonNode destinationConfiguration,
                                                                  final ConfiguredAirbyteCatalog airbyteCatalog,
                                                                  final UUID workspaceId);

}
