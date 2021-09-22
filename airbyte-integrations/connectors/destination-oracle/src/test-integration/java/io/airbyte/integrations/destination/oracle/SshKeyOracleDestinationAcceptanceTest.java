package io.airbyte.integrations.destination.oracle;

import java.nio.file.Path;

public class SshKeyOracleDestinationAcceptanceTest extends SshOracleDestinationAcceptanceTest {
    @Override
    public Path getConfigFilePath() {
        return Path.of("secrets/ssh-key-config.json");
    }
}
