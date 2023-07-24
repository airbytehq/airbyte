package io.airbyte.integrations.destination.teradata.envclient.dto;

public record EnvironmentRequest(

        String name,

        OperationRequest request

) {
}