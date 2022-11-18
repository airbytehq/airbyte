/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.models;

import java.util.Optional;

public record AttemptNormalizationStatus(int attemptNumber, Optional<Long> recordsCommitted, boolean normalizationFailed) {}
