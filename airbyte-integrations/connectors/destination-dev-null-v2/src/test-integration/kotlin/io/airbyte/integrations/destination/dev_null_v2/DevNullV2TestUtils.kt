/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import io.airbyte.cdk.command.ValidatedJsonUtils
import java.nio.file.Files
import java.nio.file.Path

object DevNullV2TestUtils {
    val loggingConfigPath: Path = Path.of("test_configs/logging.json")
    val silentConfigPath: Path = Path.of("test_configs/silent.json")

    fun configContents(configPath: Path): String = Files.readString(configPath, Charsets.UTF_8)

    val loggingConfig: DevNullV2SpecificationOss =
        ValidatedJsonUtils.parseOne(
            DevNullV2SpecificationOss::class.java,
            Files.readString(loggingConfigPath),
        )

    val silentConfig: DevNullV2SpecificationOss =
        ValidatedJsonUtils.parseOne(
            DevNullV2SpecificationOss::class.java,
            Files.readString(silentConfigPath),
        )
}
