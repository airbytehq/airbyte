package io.airbyte.config.persistence.split_secrets;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class MemorySecretPersistence implements SecretPersistence {

    final Map<SecretCoordinate, String> secretMap = new HashMap<>();

    @Override
    public Optional<String> read(SecretCoordinate coordinate) {
        return Optional.ofNullable(secretMap.get(coordinate));
    }

    @Override
    public void write(SecretCoordinate coordinate, String payload) {
        secretMap.put(coordinate, payload);
    }
}
