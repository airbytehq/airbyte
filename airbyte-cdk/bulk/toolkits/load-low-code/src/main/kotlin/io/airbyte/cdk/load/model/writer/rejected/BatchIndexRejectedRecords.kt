package io.airbyte.cdk.load.model.writer.rejected

import com.fasterxml.jackson.annotation.JsonProperty

class BatchIndexRejectedRecords(
    @JsonProperty("condition") val condition: String,
    @JsonProperty("rejections_field") val rejectionsField: List<String>,
    @JsonProperty("index_field") val indexField: List<String>,
    @JsonProperty("fields_to_report") val fieldsToReport: List<List<String>>,
) : RejectedRecords
