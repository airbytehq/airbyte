package io.airbyte.integrations.destination.snowflake

import com.google.common.io.Resources
import java.nio.file.Path

object Utils {
    fun getConfigPath(resourceName: String): Path {
        return Path.of(resourceName)
    }
}
