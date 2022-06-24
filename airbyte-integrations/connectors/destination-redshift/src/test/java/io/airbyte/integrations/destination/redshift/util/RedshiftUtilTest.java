package io.airbyte.integrations.destination.redshift.util;

import static io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants.UPLOADING_METHOD;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

public class RedshiftUtilTest {

  @Test
  @DisplayName("Should return the config when the config has uploading method")
  public void testFindS3OptionsWhenConfigHasUploadingMethod() {
    JsonNode config = mock(JsonNode.class);
    JsonNode uploadingMethod = mock(JsonNode.class);
    when(config.has(UPLOADING_METHOD)).thenReturn(true);
    when(config.get(UPLOADING_METHOD)).thenReturn(uploadingMethod);

    JsonNode result = RedshiftUtil.findS3Options(config);

    assertEquals(uploadingMethod, result);
  }

  @Test
  @DisplayName("Should return the config when the config does not have uploading method")
  public void testFindS3OptionsWhenConfigDoesNotHaveUploadingMethod() {
    JsonNode config = mock(JsonNode.class);
    when(config.has(UPLOADING_METHOD)).thenReturn(false);

    JsonNode result = RedshiftUtil.findS3Options(config);

    assertEquals(config, result);
  }

  @Test
  @DisplayName("Should return true when all of the fields are null or empty")
  public void testAnyOfS3FieldsAreNullOrEmptyWhenAllOfTheFieldsAreNullOrEmptyThenReturnTrue() {
    JsonNode jsonNode = mock(JsonNode.class);
    when(jsonNode.get("s3_bucket_name")).thenReturn(null);
    when(jsonNode.get("s3_bucket_region")).thenReturn(null);
    when(jsonNode.get("access_key_id")).thenReturn(null);
    when(jsonNode.get("secret_access_key")).thenReturn(null);

    assertTrue(RedshiftUtil.anyOfS3FieldsAreNullOrEmpty(jsonNode));
  }

  @Test
  @DisplayName("Should return false when all S3 required fields are not null or empty")
  public void testAllS3RequiredAreNotNullOrEmptyThenReturnFalse() {
    JsonNode jsonNode = mock(JsonNode.class);
    when(jsonNode.get("s3_bucket_name")).thenReturn(mock(JsonNode.class));
    when(jsonNode.get("s3_bucket_name").asText()).thenReturn("test");
    when(jsonNode.get("s3_bucket_region")).thenReturn(mock(JsonNode.class));
    when(jsonNode.get("s3_bucket_region").asText()).thenReturn("test");
    when(jsonNode.get("access_key_id")).thenReturn(mock(JsonNode.class));
    when(jsonNode.get("access_key_id").asText()).thenReturn("test");
    when(jsonNode.get("secret_access_key")).thenReturn(mock(JsonNode.class));
    when(jsonNode.get("secret_access_key").asText()).thenReturn("test");

    assertFalse(RedshiftUtil.anyOfS3FieldsAreNullOrEmpty(jsonNode));
  }
}