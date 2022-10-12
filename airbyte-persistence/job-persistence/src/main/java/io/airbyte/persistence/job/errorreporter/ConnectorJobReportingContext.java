/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.errorreporter;

import java.util.UUID;

public record ConnectorJobReportingContext(UUID jobId, String dockerImage) {}
