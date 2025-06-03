package io.airbyte.integrations.destination.shelby.http.job

data class Job (val id: String) {
    var status: JobStatus = JobStatus.UPLOADED
}
