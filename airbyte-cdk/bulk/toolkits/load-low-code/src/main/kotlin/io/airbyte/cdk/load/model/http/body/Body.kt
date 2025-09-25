package io.airbyte.cdk.load.model.http.body

import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import io.airbyte.cdk.load.model.http.body.batch.JsonBatchBody

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
@JsonSubTypes(JsonSubTypes.Type(value = JsonBatchBody::class, name = "JsonBatchBody"))
interface Body
