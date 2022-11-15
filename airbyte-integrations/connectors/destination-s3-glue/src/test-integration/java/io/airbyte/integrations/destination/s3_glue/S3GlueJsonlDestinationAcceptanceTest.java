/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3BaseJsonlDestinationAcceptanceTest;
import java.util.Map;

public class S3GlueJsonlDestinationAcceptanceTest extends S3BaseJsonlDestinationAcceptanceTest {

    @Override
    protected JsonNode getFormatConfig() {
        return Jsons.jsonNode(Map.of(
            "format_type", outputFormat,
            "compression", Jsons.jsonNode(Map.of("compression_type", "No Compression")),
            "flatten_data", true));
    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) {
        super.tearDown(testEnv);

        GlueDestinationConfig glueDestinationConfig = GlueDestinationConfig.getInstance(configJson);
        try (var glueTestClient = new GlueTestClient(glueDestinationConfig.getAWSGlueInstance())) {

            glueTestClient.purgeDatabase(glueDestinationConfig.getDatabase());

        }
    }
}
