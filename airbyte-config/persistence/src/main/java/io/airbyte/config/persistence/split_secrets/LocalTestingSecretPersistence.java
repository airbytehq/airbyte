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
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import java.io.IOException;
import java.util.Optional;

/**
 * Secrets persistence intended only for local development.
 */
public class LocalTestingSecretPersistence implements SecretPersistence {

  private final Database configDatabase;

  public LocalTestingSecretPersistence(final Database configDatabase) {
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
  public Optional<String> read(final SecretCoordinate coordinate) {
    final Optional<String> output = Exceptions.toRuntime(() -> this.configDatabase.query(ctx -> {
      final var result = ctx.fetch("SELECT payload FROM secrets WHERE coordinate = ?;", coordinate.getFullCoordinate());
      if (result.size() == 0) {
        return Optional.empty();
      } else {
        return Optional.of(result.get(0).getValue(0, String.class));
      }
    }));

    System.out.println("SECRET READ(" + coordinate.getFullCoordinate() + ") = " + output);

    return output;
  }

  @Override
  public void write(final SecretCoordinate coordinate, final String payload) {
    System.out.println("SECRET WRITE(" + coordinate.getFullCoordinate() + ", " + payload + ")");
    Exceptions.toRuntime(() -> this.configDatabase.query(ctx -> {
      int result = ctx.query("INSERT INTO secrets(coordinate,payload) VALUES(?, ?) ON CONFLICT (coordinate) DO UPDATE SET payload = ?;",
          coordinate.getFullCoordinate(), payload, payload, coordinate.getFullCoordinate()).execute();
      System.out.println("SECRET WRITE EXECUTE RESULT: " + result);
      return null;
    }));
  }

  public static void main(String[] args) throws IOException {
    final Database configDatabase = new ConfigsDatabaseInstance(
        "docker",
        "docker",
        "jdbc:postgresql://localhost:5432/airbyte")
            .getAndInitialize();
    final var persistence = new LocalTestingSecretPersistence(configDatabase);

    final var coordinate1 = new SecretCoordinate("base1", 1);
    final var coordinate2 = new SecretCoordinate("base2", 1);

    persistence.write(coordinate1, "hunter1");
    System.out.println("persistence.read(coordinate1) = " + persistence.read(coordinate1));
    System.out.println("persistence.read(coordinate2) = " + persistence.read(coordinate2));

    persistence.write(coordinate2, "hunter2");
    System.out.println("persistence.read(coordinate1) = " + persistence.read(coordinate1));
    System.out.println("persistence.read(coordinate2) = " + persistence.read(coordinate2));

    persistence.write(coordinate1, "hunter3");
    System.out.println("persistence.read(coordinate1) = " + persistence.read(coordinate1));
    System.out.println("persistence.read(coordinate2) = " + persistence.read(coordinate2));
  }

}
