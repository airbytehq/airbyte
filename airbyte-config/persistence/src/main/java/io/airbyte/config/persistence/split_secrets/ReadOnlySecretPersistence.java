package io.airbyte.config.persistence.split_secrets;

import java.util.Optional;
import java.util.function.Function;

public interface ReadOnlySecretPersistence extends Function<SecretCoordinate, Optional<String>> {

}
