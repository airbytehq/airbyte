package io.airbyte.integrations.destination.oracle;

import java.nio.file.Path;

public class SshPasswordOracleDestinationAcceptanceTest extends SshOracleDestinationAcceptanceTest{
    @Override
    public Path getConfigFilePath() {
        return Path.of("secrets/ssh-pwd-config.json");
    }
}
