package io.airbyte.integrations.source.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.kafka.format.AvroFormat;
import io.airbyte.integrations.source.kafka.format.KafkaFormat;
import org.junit.jupiter.api.Test;

import java.io.IOException;

import static org.junit.jupiter.api.Assertions.assertInstanceOf;


public class KafkaSourceTest {


    @Test
    public void testAvroformat() throws IOException {
        final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));
        final KafkaFormat kafkaFormat =KafkaFormatFactory.getFormat(configJson);
        assertInstanceOf(AvroFormat.class,kafkaFormat);
    }

}
