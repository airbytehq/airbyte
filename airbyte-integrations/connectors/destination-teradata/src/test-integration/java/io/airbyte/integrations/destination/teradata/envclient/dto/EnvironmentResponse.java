package io.airbyte.integrations.destination.teradata.envclient.dto;

import java.util.List;

public record EnvironmentResponse(

        State state,

        String region,

        // Use for subsequent environment operations i.e GET, DELETE, etc
        String name,

        // Use for connecting with JDBC driver
        String ip,

        String dnsName,

        String owner,

        String type,

        List<Service> services

) {

    record Service(

            List<Credential> credentials,

            String name,

            String url

    ) {

    }

    record Credential(

            String name,

            String value

    ) {

    }

    public enum State {

        PROVISIONING, INITIALIZING, RUNNING, STARTING, STOPPING, STOPPED, TERMINATING, TERMINATED, REPAIRING

    }

}