/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.job

data class Job(val id: String) {
    var status: JobStatus = JobStatus.UPLOADED
}
