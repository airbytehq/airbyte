/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import java.nio.file.Path
import org.junit.jupiter.api.Disabled

@Disabled
class SshPasswordMySQLDestinationAcceptanceTest : SshMySQLDestinationAcceptanceTest() {
    override val configFilePath: Path?
        get() = Path.of("secrets/ssh-pwd-config.json")

    /**
     * Legacy normalization doesn't correctly parse the SSH password (or something). All tests
     * involving the normalization container are broken. That's (mostly) fine; DV2 doesn't rely on
     * that container.
     */
    @Disabled(
        "Our dbt interface doesn't correctly parse the SSH password. Won't fix this test, since DV2 will replace normalization."
    )
    @Throws(Exception::class)
    override fun testSyncWithNormalization(messagesFilename: String, catalogFilename: String) {
        super.testSyncWithNormalization(messagesFilename, catalogFilename)
    }

    /**
     * Similar to [.testSyncWithNormalization], disable the custom dbt test.
     *
     * TODO: get custom dbt transformations working
     * https://github.com/airbytehq/airbyte/issues/33547
     */
    @Disabled(
        "Our dbt interface doesn't correctly parse the SSH password. https://github.com/airbytehq/airbyte/issues/33547 to fix this."
    )
    @Throws(Exception::class)
    override fun testCustomDbtTransformations() {
        super.testCustomDbtTransformations()
    }
}
