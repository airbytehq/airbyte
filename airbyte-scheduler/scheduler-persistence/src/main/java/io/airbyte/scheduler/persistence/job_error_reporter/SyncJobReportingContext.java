/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

public record SyncJobReportingContext(long jobId, String sourceDockerImage, String destinationDockerImage) {

}
