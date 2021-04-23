package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;

import java.nio.file.Path;

public class SnowflakeS3CopyIntegrationTest extends SnowflakeInsertIntegrationTest {
    @Override
    public JsonNode getStaticConfig() {
        final JsonNode copyConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/copy_s3_config.json")));
        Preconditions.checkArgument(SnowflakeDestination.isCopy(copyConfig));
        return copyConfig;
    }
}
