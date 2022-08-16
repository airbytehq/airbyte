/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import java.util.UUID;

public record ConnectorJobReportingContext(UUID jobId, String dockerImage) {}
