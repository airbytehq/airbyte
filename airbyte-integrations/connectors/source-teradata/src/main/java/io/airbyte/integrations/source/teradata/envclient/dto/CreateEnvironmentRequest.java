package io.airbyte.integrations.source.teradata.envclient.dto;

public record CreateEnvironmentRequest(

    String name,

    String region,

    String password

) {

}
