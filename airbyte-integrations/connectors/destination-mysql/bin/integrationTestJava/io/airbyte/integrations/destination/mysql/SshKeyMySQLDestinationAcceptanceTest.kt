/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import java.nio.file.Path
import org.junit.jupiter.api.Disabled

@Disabled
class SshKeyMySQLDestinationAcceptanceTest : SshMySQLDestinationAcceptanceTest() {
    override val configFilePath: Path?
        get() = Path.of("secrets/ssh-key-config.json")
}
