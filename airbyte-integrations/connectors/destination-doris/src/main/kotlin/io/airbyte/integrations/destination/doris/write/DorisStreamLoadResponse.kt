/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.write

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty

/** Response from Doris Stream Load API. */
@JsonIgnoreProperties(ignoreUnknown = true)
data class DorisStreamLoadResponse(
    @JsonProperty("Status") val status: String? = null,
    @JsonProperty("Message") val message: String? = null,
    @JsonProperty("NumberTotalRows") val numberTotalRows: Long = 0,
    @JsonProperty("NumberLoadedRows") val numberLoadedRows: Long = 0,
    @JsonProperty("NumberFilteredRows") val numberFilteredRows: Long = 0,
    @JsonProperty("NumberUnselectedRows") val numberUnselectedRows: Long = 0,
    @JsonProperty("LoadBytes") val loadBytes: Long = 0,
    @JsonProperty("LoadTimeMs") val loadTimeMs: Long = 0,
    @JsonProperty("ErrorURL") val errorUrl: String? = null,
    @JsonProperty("Label") val label: String? = null,
    @JsonProperty("ExistingJobStatus") val existingJobStatus: String? = null,
) {
    fun isSuccess(): Boolean = status == LoadStatus.SUCCESS || status == LoadStatus.PUBLISH_TIMEOUT

    fun isLabelAlreadyExists(): Boolean = status == LoadStatus.LABEL_ALREADY_EXISTS

    fun isLabelAlreadyExistsAndSuccess(): Boolean =
        isLabelAlreadyExists() && existingJobStatus == "FINISHED"

    object LoadStatus {
        const val SUCCESS = "Success"
        const val PUBLISH_TIMEOUT = "Publish Timeout"
        const val LABEL_ALREADY_EXISTS = "Label Already Exists"
        const val FAIL = "Fail"
    }
}
