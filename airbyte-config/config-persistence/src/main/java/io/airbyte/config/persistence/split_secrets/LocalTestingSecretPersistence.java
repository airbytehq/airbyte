/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.Database;
import java.sql.SQLException;
import java.util.Optional;

/**
 * Secrets persistence intended only for local development.
 */
public class LocalTestingSecretPersistence implements SecretPersistence {

  private final Database configDatabase;

  private boolean initialized = false;

  public LocalTestingSecretPersistence(final Database configDatabase) {
    this.configDatabase = configDatabase;
  }

  @Override
  public void initialize() throws SQLException {
    if (!initialized) {
      this.configDatabase.query(ctx -> {
        ctx.execute("CREATE TABLE IF NOT EXISTS secrets ( coordinate TEXT PRIMARY KEY, payload TEXT);");
        return null;
      });
      initialized = true;
    }
  }

  @Override
  public Optional<String> read(final SecretCoordinate coordinate) {
    return Exceptions.toRuntime(() -> this.configDatabase.query(ctx -> {
      initialize();
      final var result = ctx.fetch("SELECT payload FROM secrets WHERE coordinate = ?;", coordinate.getFullCoordinate());
      if (result.size() == 0) {
        return Optional.empty();
      } else {
        return Optional.of(result.get(0).getValue(0, String.class));
      }
    }));
  }

  @Override
  public void write(final SecretCoordinate coordinate, final String payload) {
    Exceptions.toRuntime(() -> this.configDatabase.query(ctx -> {
      initialize();
      ctx.query("INSERT INTO secrets(coordinate,payload) VALUES(?, ?) ON CONFLICT (coordinate) DO UPDATE SET payload = ?;",
          coordinate.getFullCoordinate(), payload, payload, coordinate.getFullCoordinate()).execute();
      return null;
    }));
  }

}
