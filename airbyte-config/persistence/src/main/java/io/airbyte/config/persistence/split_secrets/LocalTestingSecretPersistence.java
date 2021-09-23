/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.config.persistence.split_secrets;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.Database;
import java.util.Optional;

/**
 * Secrets persistence intended only for local development.
 */
public class LocalTestingSecretPersistence implements SecretPersistence {

  // todo: maybe just create and write to a db table in here instead of using config persistences?
  // then it'd be good for testing?
  private final Database configDatabase;

  public LocalTestingSecretPersistence(Database configDatabase) {
    this.configDatabase = configDatabase;

    System.out.println("SECRET STORE INITIALIZE LocalTestingSecretPersistence");
    Exceptions.toRuntime(() -> {
      this.configDatabase.query(ctx -> {
        ctx.execute("CREATE TABLE IF NOT EXISTS secrets ( coordinate TEXT PRIMARY KEY, payload TEXT);");
        return null;
      });
    });
  }

  @Override
  public Optional<String> read(SecretCoordinate coordinate) {
    final Optional<String> output = Exceptions.toRuntime(() -> this.configDatabase.query(ctx -> {
      final var result = ctx.resultQuery("SELECT payload FROM secrets WHERE coordinate = ?;", coordinate.getFullCoordinate()).fetch();
      if (result.size() == 0) {
        return Optional.empty();
      } else {
        return Optional.of(result.get(0).get("payload", String.class));
      }
    }));

    System.out.println("SECRET READ(" + coordinate.getFullCoordinate() + ") = " + output);

    return output;
  }

  @Override
  public void write(SecretCoordinate coordinate, String payload) {
    System.out.println("SECRET WRITE(" + coordinate.getFullCoordinate() + ", " + payload + ")");
    Exceptions.toRuntime(() -> this.configDatabase.query(ctx -> {
      ctx.query("INSERT INTO secrets(coordinate,payload) VALUES(?, ?) ON CONFLICT (coordinate) DO UPDATE SET payload = ? WHERE coordinate = ?;",
          coordinate.getFullCoordinate(), payload, payload, coordinate.getFullCoordinate());

      return null;
    }));
  }

}
