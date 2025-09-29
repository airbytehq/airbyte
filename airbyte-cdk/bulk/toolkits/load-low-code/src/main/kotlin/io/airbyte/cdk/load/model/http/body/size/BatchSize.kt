package io.airbyte.cdk.load.model.http.body.size

import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
@JsonSubTypes(
    JsonSubTypes.Type(value = RequestMemoryBatchSize::class, name = "RequestMemoryBatchSize")
)
sealed interface BatchSize
