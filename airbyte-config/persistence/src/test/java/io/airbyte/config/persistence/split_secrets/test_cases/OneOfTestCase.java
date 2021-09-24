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

package io.airbyte.config.persistence.split_secrets.test_cases;

import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHelpersTest;
import io.airbyte.config.persistence.split_secrets.SecretsTestCase;
import java.util.Map;
import java.util.function.Consumer;

public class OneOfTestCase implements SecretsTestCase {

  @Override
  public String getName() {
    return "oneof";
  }

  @Override
  public Map<SecretCoordinate, String> getFirstSecretMap() {
    return Map.of(
        new SecretCoordinate("airbyte_workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(0), 1), "hunter1",
        new SecretCoordinate("airbyte_workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(1), 1), "hunter2");
  }

  @Override
  public Map<SecretCoordinate, String> getSecondSecretMap() {
    return Map.of(
        new SecretCoordinate("airbyte_workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(0), 2), "hunter3",
        new SecretCoordinate("airbyte_workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(1), 2), "hunter4");
  }

  @Override
  public Consumer<SecretPersistence> getPersistenceUpdater() {
    return secretPersistence -> {
      secretPersistence.write(
          new SecretCoordinate("airbyte_workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(0), 1),
          "hunter1");
      secretPersistence.write(
          new SecretCoordinate("airbyte_workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(1), 1),
          "hunter2");
    };
  }

}
