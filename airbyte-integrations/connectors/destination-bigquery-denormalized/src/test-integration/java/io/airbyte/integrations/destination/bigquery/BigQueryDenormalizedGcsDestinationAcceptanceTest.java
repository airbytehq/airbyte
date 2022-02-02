/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE;
import static io.airbyte.integrations.standardtest.destination.DateTimeUtils.DATE_TIME;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Map;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.stream.StreamSupport;
import org.apache.commons.lang3.StringUtils;
import org.junit.jupiter.api.Assertions;

public class BigQueryDenormalizedGcsDestinationAcceptanceTest extends BigQueryDenormalizedDestinationAcceptanceTest {

  @Override
  protected JsonNode createConfig() throws IOException {
    final String credentialsJsonString = Files.readString(CREDENTIALS_PATH);

    final JsonNode fullConfigFromSecretFileJson = Jsons.deserialize(credentialsJsonString);
    final JsonNode bigqueryConfigFromSecretFile = fullConfigFromSecretFileJson.get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);
    final JsonNode gcsConfigFromSecretFile = fullConfigFromSecretFileJson.get(BigQueryConsts.GCS_CONFIG);

    final String projectId = bigqueryConfigFromSecretFile.get(CONFIG_PROJECT_ID).asText();
    final String datasetLocation = "US";

    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);

    final JsonNode gcsCredentialFromSecretFile = gcsConfigFromSecretFile.get(BigQueryConsts.CREDENTIAL);
    final JsonNode credential = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CREDENTIAL_TYPE, gcsCredentialFromSecretFile.get(BigQueryConsts.CREDENTIAL_TYPE))
        .put(BigQueryConsts.HMAC_KEY_ACCESS_ID, gcsCredentialFromSecretFile.get(BigQueryConsts.HMAC_KEY_ACCESS_ID))
        .put(BigQueryConsts.HMAC_KEY_ACCESS_SECRET, gcsCredentialFromSecretFile.get(BigQueryConsts.HMAC_KEY_ACCESS_SECRET))
        .build());

    final JsonNode loadingMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.METHOD, BigQueryConsts.GCS_STAGING)
        .put(BigQueryConsts.GCS_BUCKET_NAME, gcsConfigFromSecretFile.get(BigQueryConsts.GCS_BUCKET_NAME))
        .put(BigQueryConsts.GCS_BUCKET_PATH, gcsConfigFromSecretFile.get(BigQueryConsts.GCS_BUCKET_PATH).asText() + System.currentTimeMillis())
        .put(BigQueryConsts.PART_SIZE, gcsConfigFromSecretFile.get(BigQueryConsts.PART_SIZE))
        .put(BigQueryConsts.CREDENTIAL, credential)
        .build());

    return Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_CREDS, bigqueryConfigFromSecretFile.toString())
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, datasetLocation)
        .put(BigQueryConsts.LOADING_METHOD, loadingMethod)
        .build());
  }


  @Override
  public boolean requiresDateTimeConversionForSync() {
    return true;
  }

  @Override
  public void convertDateTime(ObjectNode data, Map<String, String> dateTimeFieldNames) {
    var fields = StreamSupport.stream(Spliterators.spliteratorUnknownSize(data.fields(),
        Spliterator.ORDERED), false).toList();
    data.removeAll();
    fields.forEach(field -> {
      var key = field.getKey();
      if (dateTimeFieldNames.containsKey(key)) {
        switch (dateTimeFieldNames.get(key)) {
          case DATE_TIME -> data.put(key.toLowerCase(), DateTimeUtils.getEpochMicros(field.getValue().asText()));
          case DATE -> data.put(key.toLowerCase(), DateTimeUtils.convertToDateFormat(field.getValue().asText()));
        }
      } else {
        data.set(key.toLowerCase(), field.getValue());
      }
    });
  }

  @Override
  protected void assertSameValue(String key,
                                 JsonNode expectedValue,
                                 JsonNode actualValue) {
    if (DATE_TIME.equals(dateTimeFieldNames.getOrDefault(key, StringUtils.EMPTY))) {
      Assertions.assertEquals(expectedValue.asLong() / 1000000, actualValue.asLong());
    } else {
      super.assertSameValue(key, expectedValue, actualValue);
    }
  }

}
