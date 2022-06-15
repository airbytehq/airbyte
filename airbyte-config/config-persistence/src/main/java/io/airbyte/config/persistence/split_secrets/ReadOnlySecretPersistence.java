/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import java.util.Optional;

/**
 * Provides a read-only interface to a backing secrets store similar to {@link SecretPersistence}.
 * In practice, the functionality should be provided by a {@link SecretPersistence#read} function.
 */
@FunctionalInterface
public interface ReadOnlySecretPersistence {

  Optional<String> read(SecretCoordinate coordinate);

}
