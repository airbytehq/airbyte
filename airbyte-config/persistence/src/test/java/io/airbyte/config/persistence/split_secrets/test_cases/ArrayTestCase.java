package io.airbyte.config.persistence.split_secrets.test_cases;

import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHelpersTest;
import io.airbyte.config.persistence.split_secrets.SecretsTestCase;

import java.util.Map;
import java.util.function.Consumer;

public class ArrayTestCase implements SecretsTestCase {

    @Override
    public String getName() {
        return "array";
    }

    @Override
    public Map<SecretCoordinate, String> getFirstSecretMap() {
        return Map.of(
                new SecretCoordinate("workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(0), 1), "key1",
                new SecretCoordinate("workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(1), 1), "key2",
                new SecretCoordinate("workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(2), 1), "key3");
    }

    @Override
    public Map<SecretCoordinate, String> getSecondSecretMap() {
        return Map.of(
                new SecretCoordinate("workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(0), 2), "key1",
                new SecretCoordinate("workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(1), 2), "key2",
                new SecretCoordinate("workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(2), 2), "key3");
    }

    @Override
    public Consumer<SecretPersistence> getPersistenceUpdater() {
        return secretPersistence -> {
            secretPersistence.write(new SecretCoordinate("workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(0), 1), "key1");
            secretPersistence.write(new SecretCoordinate("workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(1), 1), "key2");
            secretPersistence.write(new SecretCoordinate("workspace_" + SecretsHelpersTest.WORKSPACE_ID + "_secret_" + SecretsHelpersTest.UUIDS.get(2), 1), "key3");
        };
    }
}
