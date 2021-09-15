package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.protocol.models.ConnectorSpecification;

import java.util.UUID;
import java.util.function.Supplier;

public class SecretsHelpers {

    // todo: double check oauth stuff that's already in place
    // todo: create an in memory singleton map secrets store implementation for testing
    // todo: create a separate persistence for secrets that doesn't have config types, is just string to string and allows configuration for a specific prefix

    // todo: CREATION spec + full config -> coordconfig+secrets
    public static SplitSecretConfig split(Supplier<UUID> uuidSupplier, UUID workspaceId, JsonNode fullConfig, ConnectorSpecification spec) {



        // todo: get paths for all secrets in the spec

        // todo: one by one, create coordinates and payloads for each spec
        // todo: construct the partial config

        // todo: should we persist things inside here or outside? -> should be inside and should fill the partial spec with coordinates
        // todo: come up with a better name than partialConfig

//        return new SplitSecretConfig(partialConfig, secretIdToPayload);

        return null;
    }

    // todo: UPDATES old coordconfig+spec+ full config -> coordconfig+secrets
    public static SplitSecretConfig splitUpdate(UUID workspaceId, JsonNode oldPartialConfig, JsonNode newFullConfig, ConnectorSpecification spec) {
        // todo: only update if the underlying secret changed value? test this specifically
        return null;
    }

    // todo: READ coordconfig+secets persistence -> full config
    // todo: we'll want permissioning here at some point
    public static JsonNode combine(JsonNode partialConfig, ConfigPersistence secretsPersistence) {
        return null;
    }

    // todo: figure out oauth here
    // todo: test edge cases for json path definitino -> maybe can keep as a tree type or something
}
