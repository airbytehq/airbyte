/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.worker.normalization;

import io.airbyte.commons.worker.Worker;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;

public interface NormalizationWorker extends Worker<NormalizationInput, NormalizationSummary> {}
