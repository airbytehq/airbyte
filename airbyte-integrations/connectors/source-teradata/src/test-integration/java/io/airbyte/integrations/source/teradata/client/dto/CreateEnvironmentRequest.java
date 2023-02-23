package io.airbyte.integrations.source.teradata.client.dto;

public record CreateEnvironmentRequest(

    String name,

    String region,

    String password

) {

}
