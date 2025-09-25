package io.airbyte.cdk.load.model.http.body.size

import com.fasterxml.jackson.annotation.JsonProperty;


// TODO eventually we can add the units so that the size does not always need to be bytes
data class RequestMemoryBatchSize(@JsonProperty("amount") val amount: Int) : BatchSize
