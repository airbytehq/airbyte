package io.airbyte.config.persistence.split_secrets;

import java.util.Optional;

public class NoOpSecretPersistence implements SecretPersistence {
    @Override
    public Optional<String> read(SecretCoordinate coordinate) {
        return Optional.empty();
    }

    @Override
    public void write(SecretCoordinate coordinate, String payload) {
        // no-op
    }
}
