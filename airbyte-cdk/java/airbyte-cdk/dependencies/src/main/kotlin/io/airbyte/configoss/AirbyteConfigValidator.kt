/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.configoss

import io.airbyte.validation.json.AbstractSchemaValidator
import java.nio.file.Path

class AirbyteConfigValidator : AbstractSchemaValidator<ConfigSchema>() {
    override fun getSchemaPath(configType: ConfigSchema): Path {
        return configType.configSchemaFile.toPath()
    }

    companion object {
        val AIRBYTE_CONFIG_VALIDATOR: AirbyteConfigValidator = AirbyteConfigValidator()
    }
}
