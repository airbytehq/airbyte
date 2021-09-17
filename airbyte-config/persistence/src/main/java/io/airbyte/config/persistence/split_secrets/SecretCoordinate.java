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
import java.util.UUID;

public class SecretCoordinate {

  private final String coordinateBase;
  private final long version;

  // todo: Should the version be exposed here? WHat should this look like for OAuth secrets?
  // todo: Should everything use the smae persistence interface with the config writing?
  public SecretCoordinate(final String coordinateBase, final long version) {
    this.coordinateBase = coordinateBase;
    this.version = version;
  }

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

  // todo: test
  @Override
  public String toString() {
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

  @Override
  public int hashCode() {
    return Objects.hash(toString());
  }

}
