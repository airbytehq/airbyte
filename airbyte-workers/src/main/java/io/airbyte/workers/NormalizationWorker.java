/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;

public interface NormalizationWorker extends Worker<NormalizationInput, NormalizationSummary> {}
