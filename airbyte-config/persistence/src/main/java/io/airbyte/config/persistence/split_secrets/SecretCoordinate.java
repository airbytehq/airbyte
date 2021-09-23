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

import com.google.api.client.util.Preconditions;
import java.util.Objects;

/**
 * A secret coordinate represents a specific secret at a specific version stored within a
 * {@link SecretPersistence}.
 *
 * We use "coordinate base" to refer to a string reference to a secret without versioning
 * information. We use "full coordinate" to refer to a string reference that includes both the
 * coordinate base and version-specific information. You should be able to go from a "full
 * coordinate" to a coordinate object and back without loss of information.
 *
 * Example coordinate base:
 * airbyte_workspace_e0eb0554-ffe0-4e9c-9dc0-ed7f52023eb2_secret_9eba44d8-51e7-48f1-bde2-619af0e42c22
 *
 * Example full coordinate:
 * airbyte_workspace_e0eb0554-ffe0-4e9c-9dc0-ed7f52023eb2_secret_9eba44d8-51e7-48f1-bde2-619af0e42c22_v1
 *
 * This coordinate system was designed to work well with Google Secrets Manager but should work with
 * other secret storage backends as well.
 */
public class SecretCoordinate {

  private final String coordinateBase;
  private final long version;

  public SecretCoordinate(final String coordinateBase, final long version) {
    this.coordinateBase = coordinateBase;
    this.version = version;
  }

  /**
   * Used to turn a full string coordinate into a coordinate object using a full coordinate generated
   * by {@link SecretsHelpers#getCoordinate}.
   *
   * This will likely need refactoring if we end up using a secret store that doesn't allow the same
   * format of full coordinate.
   *
   * @param fullCoordinate coordinate with version
   * @return secret coordinate object
   */
  public static SecretCoordinate fromFullCoordinate(String fullCoordinate) {
    final var splits = fullCoordinate.split("_v");
    Preconditions.checkArgument(splits.length == 2);

    return new SecretCoordinate(splits[0], Long.parseLong(splits[1]));
  }

  public String getCoordinateBase() {
    return coordinateBase;
  }

  public long getVersion() {
    return version;
  }

  public String getFullCoordinate() {
    return coordinateBase + "_v" + version;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o)
      return true;
    if (o == null || getClass() != o.getClass())
      return false;
    SecretCoordinate that = (SecretCoordinate) o;
    return toString().equals(that.toString());
  }

  /**
   * The hash code is computed using the {@link SecretCoordinate#getFullCoordinate} because the full
   * secret coordinate should be a valid unique representation of the secret coordinate.
   */
  @Override
  public int hashCode() {
    return Objects.hash(getFullCoordinate());
  }

}
