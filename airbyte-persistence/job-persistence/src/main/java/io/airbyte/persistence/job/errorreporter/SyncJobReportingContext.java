/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.errorreporter;

public record SyncJobReportingContext(long jobId, String sourceDockerImage, String destinationDockerImage) {

}
