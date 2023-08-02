package io.airbyte.integrations.destination.teradata.envclient.dto;

public record CreateEnvironmentRequest(

        String name,

        String region,

        String password

) {

}
