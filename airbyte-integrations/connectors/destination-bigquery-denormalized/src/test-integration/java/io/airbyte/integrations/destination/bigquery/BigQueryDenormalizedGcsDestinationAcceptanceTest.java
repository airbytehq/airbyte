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
import io.airbyte.integrations.standardtest.destination.DateTimeUtils;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

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
    for (String path : dateTimeFieldNames.keySet()) {
      if (!data.at(path).isMissingNode() && DateTimeUtils.isDateTimeValue(data.at(path).asText())) {
        var pathFields = new ArrayList<>(Arrays.asList(path.split("/")));
        pathFields.remove(0); // first element always empty string
        // if pathFields.size() == 1 -> /field else /field/nestedField..
        var pathWithoutLastField = pathFields.size() == 1 ? "/" + pathFields.get(0)
            : "/" + String.join("/", pathFields.subList(0, pathFields.size() - 1));
        switch (dateTimeFieldNames.get(path)) {
          case DATE_TIME -> {
            if (pathFields.size() == 1) {
              var result = String.valueOf(new BigDecimal(DateTimeUtils.getEpochMicros(data.at(path).asText()) / 1000).divide(new BigDecimal(1000)));
              result = !result.contains(".") ? result + ".0" : result;
              data.put(pathFields.get(0).toLowerCase(), result);

            } else {
              var result = String.valueOf(new BigDecimal(DateTimeUtils.getEpochMicros(data.at(path).asText()) / 1000).divide(new BigDecimal(1000)));
              result = !result.contains(".") ? result + ".0" : result;
              ((ObjectNode) data.at(pathWithoutLastField)).put(pathFields.get(pathFields.size() - 1).toLowerCase(),
                  result);
            }
          }
          case DATE -> {
            if (pathFields.size() == 1)
              data.put(pathFields.get(0).toLowerCase(),
                  DateTimeUtils.convertToDateFormat(data.get(pathFields.get(0)).asText()));
            else {
              ((ObjectNode) data.at(pathWithoutLastField)).put(
                  pathFields.get(pathFields.size() - 1).toLowerCase(),
                  DateTimeUtils.convertToDateFormat((data.at(path).asText())));
            }
          }
        }
      }
    }
  }

  @Override
  protected void deserializeNestedObjects(List<AirbyteMessage> messages, List<AirbyteRecordMessage> actualMessages) {
    for (AirbyteMessage message : messages) {
      if (message.getType() == Type.RECORD) {
        var iterator = message.getRecord().getData().fieldNames();
        if (iterator.hasNext()) {
          var fieldName = iterator.next();
          if (message.getRecord().getData().get(fieldName).isContainerNode()) {
            message.getRecord().getData().get(fieldName).fieldNames().forEachRemaining(f -> {
              var data = message.getRecord().getData().get(fieldName).get(f);
              ((ObjectNode) message.getRecord().getData()).put(fieldName,
                  String.format("[FieldValue{attribute=PRIMITIVE, value=%s}]", data.asText()));
            });
          }
        }
      }
    }
  }

}
