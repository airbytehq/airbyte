/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.io.IOs.readFile
import io.airbyte.commons.json.Jsons.deserialize
import java.nio.file.Path
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class RedshiftS3StagingRawSchemaOverrideDisableTypingDedupingTest :
    AbstractRedshiftTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return deserialize(
            readFile(Path.of("secrets/1s1t_config_staging_raw_schema_override.json"))
        )
            as ObjectNode
    }

    override val rawSchema: String
        get() = "overridden_raw_dataset"

    override fun disableFinalTableComparison(): Boolean {
        return true
    }

    @Disabled @Test override fun identicalNameSimultaneousSync() {}
}
