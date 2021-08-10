/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.s3;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.DeleteObjectsResult;
import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.csv.S3CsvOutputFormatter;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import org.apache.commons.csv.QuoteMode;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class S3CsvDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory
      .getLogger(S3CsvDestinationAcceptanceTest.class);
  private static final ObjectMapper mapper = new ObjectMapper();

  private JsonNode configJson;
  private S3DestinationConfig config;
  private AmazonS3 s3Client;

  /**
   * Convert json_schema to a map from field name to field types.
   */
  private static Map<String, String> getFieldTypes(JsonNode streamSchema) {
    Map<String, String> fieldTypes = new HashMap<>();
    JsonNode fieldDefinitions = streamSchema.get("properties");
    Iterator<Entry<String, JsonNode>> iterator = fieldDefinitions.fields();
    while (iterator.hasNext()) {
      Map.Entry<String, JsonNode> entry = iterator.next();
      fieldTypes.put(entry.getKey(), entry.getValue().get("type").asText());
    }
    return fieldTypes;
  }

  private static Optional<Number> parseNumber(String input) {
    try {
      double number = Double.parseDouble(input);
      if (number % 1 == 0) {
        return Optional.of((int) number);
      } else {
        return Optional.of(number);
      }
    } catch (Exception e) {
      return Optional.empty();
    }
  }

  private static JsonNode getJsonNode(Map<String, String> input, Map<String, String> fieldTypes) {
    ObjectNode json = mapper.createObjectNode();

    if (input.containsKey(JavaBaseConstants.COLUMN_NAME_DATA)) {
      return Jsons.deserialize(input.get(JavaBaseConstants.COLUMN_NAME_DATA));
    }

    for (Map.Entry<String, String> entry : input.entrySet()) {
      String key = entry.getKey();
      if (key.equals(JavaBaseConstants.COLUMN_NAME_AB_ID) || key
          .equals(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)) {
        continue;
      }
      String value = entry.getValue();
      if (value == null || value.equals("")) {
        continue;
      }
      String type = fieldTypes.get(key);
      switch (type) {
        case "boolean" -> json.put(key, Boolean.valueOf(value));
        case "integer" -> json.put(key, Integer.valueOf(value));
        case "number" -> {
          Optional<Number> numValue = parseNumber(value);
          if (numValue.isPresent()) {
            if (numValue.get() instanceof Integer) {
              json.put(key, (int) numValue.get());
            } else {
              json.put(key, (double) numValue.get());
            }
          } else {
            json.put(key, value);
          }
        }
        default -> json.put(key, value);
      }
    }
    return json;
  }

  private static JsonNode getBaseConfigJson() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-s3:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    JsonNode baseJson = getBaseConfigJson();
    JsonNode failCheckJson = Jsons.clone(baseJson);
    // invalid credential
    ((ObjectNode) failCheckJson).put("access_key_id", "fake-key");
    ((ObjectNode) failCheckJson).put("secret_access_key", "fake-secret");
    return failCheckJson;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws IOException {
    String outputPrefix = S3CsvOutputFormatter
        .getOutputPrefix(config.getBucketPath(), namespace, streamName);
    List<S3ObjectSummary> objectSummaries = s3Client
        .listObjects(config.getBucketName(), outputPrefix)
        .getObjectSummaries()
        .stream()
        .sorted(Comparator.comparingLong(o -> o.getLastModified().getTime()))
        .collect(Collectors.toList());
    LOGGER.info(
        "All objects: {}",
        objectSummaries.stream().map(o -> String.format("%s/%s", o.getBucketName(), o.getKey())).collect(Collectors.toList()));

    Map<String, String> fieldTypes = getFieldTypes(streamSchema);
    List<JsonNode> jsonRecords = new LinkedList<>();

    for (S3ObjectSummary objectSummary : objectSummaries) {
      S3Object object = s3Client.getObject(objectSummary.getBucketName(), objectSummary.getKey());
      Reader in = new InputStreamReader(object.getObjectContent(), StandardCharsets.UTF_8);
      Iterable<CSVRecord> records = CSVFormat.DEFAULT
          .withQuoteMode(QuoteMode.NON_NUMERIC)
          .withFirstRecordAsHeader()
          .parse(in);
      StreamSupport.stream(records.spliterator(), false)
          .forEach(r -> jsonRecords.add(getJsonNode(r.toMap(), fieldTypes)));
    }

    return jsonRecords;
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    JsonNode baseConfigJson = getBaseConfigJson();
    // Set a random s3 bucket path for each integration test
    JsonNode configJson = Jsons.clone(baseConfigJson);
    String testBucketPath = String.format(
        "%s_%s",
        configJson.get("s3_bucket_path").asText(),
        RandomStringUtils.randomAlphanumeric(5));
    ((ObjectNode) configJson).put("s3_bucket_path", testBucketPath);
    this.configJson = configJson;
    this.config = S3DestinationConfig.getS3DestinationConfig(configJson);
    LOGGER.info("Test full path: {}/{}", config.getBucketName(), config.getBucketPath());

    AWSCredentials awsCreds = new BasicAWSCredentials(config.getAccessKeyId(),
        config.getSecretAccessKey());
    this.s3Client = AmazonS3ClientBuilder.standard()
        .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
        .withRegion(config.getBucketRegion())
        .build();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    List<KeyVersion> keysToDelete = new LinkedList<>();
    List<S3ObjectSummary> objects = s3Client
        .listObjects(config.getBucketName(), config.getBucketPath())
        .getObjectSummaries();
    for (S3ObjectSummary object : objects) {
      keysToDelete.add(new KeyVersion(object.getKey()));
    }

    if (keysToDelete.size() > 0) {
      LOGGER.info("Tearing down test bucket path: {}/{}", config.getBucketName(),
          config.getBucketPath());
      DeleteObjectsResult result = s3Client
          .deleteObjects(new DeleteObjectsRequest(config.getBucketName()).withKeys(keysToDelete));
      LOGGER.info("Deleted {} file(s).", result.getDeletedObjects().size());
    }
  }

}
