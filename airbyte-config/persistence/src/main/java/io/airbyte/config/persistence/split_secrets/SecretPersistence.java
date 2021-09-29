/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import java.util.Optional;

/**
 * Provides the ability to read and write secrets to a backing store. Assumes that secret payloads
 * are always strings. See {@link SecretCoordinate} for more information on how secrets are
 * identified.
 */
public interface SecretPersistence {

  Optional<String> read(SecretCoordinate coordinate);

  void write(SecretCoordinate coordinate, String payload);

}
