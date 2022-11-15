package io.airbyte.integrations.destination.s3_glue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3BaseJsonlGzipDestinationAcceptanceTest;
import java.util.Map;

public class S3GlueJsonlGzipDestinationAcceptanceTest extends S3BaseJsonlGzipDestinationAcceptanceTest {

    @Override
    protected JsonNode getFormatConfig() {
        // config without compression defaults to GZIP
        return Jsons.jsonNode(Map.of(
            "format_type", outputFormat,
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
