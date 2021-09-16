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

import java.util.Objects;
import java.util.UUID;

public class GsmSecretCoordinate {

  private final UUID workspaceId;
  private final UUID secretId;

  // todo: Should the version be exposed here? WHat should this look like for OAuth secrets?
  // todo: Should everything use the smae persistence interface with the config writing?
  public GsmSecretCoordinate(final UUID workspaceId, final UUID secretId) {
    this.workspaceId = workspaceId;
    this.secretId = secretId;
  }

  @Override
  public String toString() {
    return "workspace_" + workspaceId + "_secret_" + secretId;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o)
      return true;
    if (o == null || getClass() != o.getClass())
      return false;
    GsmSecretCoordinate that = (GsmSecretCoordinate) o;
    return toString().equals(that.toString());
  }

  @Override
  public int hashCode() {
    return Objects.hash(toString());
  }

}
