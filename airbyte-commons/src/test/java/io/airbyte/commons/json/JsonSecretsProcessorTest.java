package io.airbyte.commons.json;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.resources.MoreResources;
import org.junit.jupiter.api.Test;

import java.io.IOException;

import static org.junit.jupiter.api.Assertions.*;

public class JsonSecretsProcessorTest {

  JsonSecretsProcessor processor = new JsonSecretsProcessor();

  @Test
  public void testRemoveSecrets() throws IOException {
    JsonNode obj = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", "donttellanyone")
        .put("secret2", 12345).build());
    JsonNode schema = Jsons.deserialize(MoreResources.readResource("secrets_json_schema.json"));

    JsonNode sanitized = processor.removeSecrets(obj, schema);

    JsonNode expected = Jsons.jsonNode(ImmutableMap.of("field1", "value1", "field2", 2));
    assertEquals(expected, sanitized);
  }

  @Test
  public void testRemoveSecretsNotInObj() throws IOException {
    JsonNode schema = Jsons.deserialize(MoreResources.readResource("secrets_json_schema.json"));
    JsonNode obj = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2).build());

    JsonNode actual = processor.removeSecrets(obj, schema);

    // Didn't have secrets, no fields should have been impacted.
    assertEquals(obj, actual);
  }

  @Test
  public void testCopySecrets() throws IOException {
    JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("additional_field", "dont_copy_me")
        .put("secret1", "donttellanyone")
        .put("secret2", 12345)
        .build());

    JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .build());

    JsonNode schema = Jsons.deserialize(MoreResources.readResource("secrets_json_schema.json"));

    JsonNode actual = processor.copySecrets(src, dst, schema);

    JsonNode expected = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("secret1", "donttellanyone")
        .put("secret2", 12345)
        .build());

    assertEquals(expected, actual);
  }

  @Test
  public void testCopySecretsNotInSrc() throws IOException {
    JsonNode schema = Jsons.deserialize(MoreResources.readResource("secrets_json_schema.json"));
    JsonNode src = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .put("additional_field", "dont_copy_me")
        .build());

    JsonNode dst = Jsons.jsonNode(ImmutableMap.builder()
        .put("field1", "value1")
        .put("field2", 2)
        .build());

    JsonNode expected = dst.deepCopy();
    JsonNode actual = processor.copySecrets(src, dst, schema);

    assertEquals(expected, actual);
  }

}
