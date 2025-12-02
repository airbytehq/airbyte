/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.command.ValidatedJsonUtils
import java.nio.file.Files
import java.nio.file.Path

object DevNullTestUtils {
    /*
     * Most destinations probably want a function to randomize the config:
     * fun getS3StagingConfig(randomizedNamespace: String) {
     *   return baseConfig.withDefaultNamespace(randomizedNamespace)
     * }
     * but destination-e2e doesn't actually _do_ anything, so we can just
     * use a constant config
     */
    /*
     * destination-e2e-test has no real creds, so we just commit these configs
     * directly on git.
     * most real destinations will put their configs in GSM,
     * so their paths would be `secrets/blah.json`.
     */
    val loggingConfigPath: Path = Path.of("test_configs/logging.json")
    val silentConfigPath: Path = Path.of("test_configs/silent.json")
    fun configContents(configPath: Path): String = Files.readString(configPath, Charsets.UTF_8)
    val loggingConfig: DevNullSpecification =
        ValidatedJsonUtils.parseOne(
            DevNullSpecificationOss::class.java,
            Files.readString(loggingConfigPath),
        )
}
