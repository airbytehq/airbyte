package io.airbyte.config.persistence.split_secrets;

import java.util.Optional;

public interface SecretPersistence {
    Optional<String> read(SecretCoordinate coordinate);

    void write(SecretCoordinate coordinate, String payload);
}
