/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.io.IOs.readFile
import io.airbyte.commons.json.Jsons.deserialize
import java.nio.file.Path

class RedshiftS3StagingTypingDedupingTest : AbstractRedshiftTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return deserialize(readFile(Path.of("secrets/1s1t_config_staging.json"))) as ObjectNode
    }
}
