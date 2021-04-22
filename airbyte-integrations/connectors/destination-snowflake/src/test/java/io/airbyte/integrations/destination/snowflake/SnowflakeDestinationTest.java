package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;


public class SnowflakeDestinationTest {

    private static final ObjectMapper mapper = new ObjectMapper();

    @Test
    @DisplayName("When given S3 credentials should use COPY")
    public void useCopyStrategyTest() {
        var stubLoadingMethod = mapper.createObjectNode();
        stubLoadingMethod.put("s3_bucket_name", "fake-bucket");
        stubLoadingMethod.put("access_key_id", "test");
        stubLoadingMethod.put("secret_access_key", "test key");

        var stubConfig = mapper.createObjectNode();
        stubConfig.set("loading_method", stubLoadingMethod);

        assertTrue(SnowflakeDestination.isCopy(stubConfig));
    }

    @Test
    @DisplayName("When not given S3 credentials should use INSERT")
    public void useInsertStrategyTest() {
        var stubLoadingMethod = mapper.createObjectNode();
        var stubConfig = mapper.createObjectNode();
        stubConfig.set("loading_method", stubLoadingMethod);
        assertFalse(SnowflakeDestination.isCopy(stubConfig));
    }

}
