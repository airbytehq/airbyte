/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.command.ValidatedJsonUtils
import java.nio.file.Files
import java.nio.file.Path

object S3V2TestUtils {
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
    const val MINIMAL_CONFIG_PATH = "secrets/s3_dest_v2_minimal_required_config.json"
    val minimalConfig: S3V2Specification =
        ValidatedJsonUtils.parseOne(
            S3V2Specification::class.java,
            Files.readString(Path.of(MINIMAL_CONFIG_PATH)),
        )
}
