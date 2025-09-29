package io.airbyte.cdk.load.model.writer.rejected

import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
@JsonSubTypes(
    JsonSubTypes.Type(value = BatchIndexRejectedRecords::class, name = "BatchIndexRejectedRecords")
)
interface RejectedRecords {}
