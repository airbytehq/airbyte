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

import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectReader;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.parquet.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.parquet.JsonToAvroSchemaConverter;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetWriter;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.LinkedList;
import java.util.List;
import org.apache.avro.generic.GenericData;
import org.apache.hadoop.conf.Configuration;
import org.apache.parquet.avro.AvroReadSupport;
import org.apache.parquet.hadoop.ParquetReader;
import tech.allegro.schema.json2avro.converter.JsonAvroConverter;

public class S3ParquetDestinationAcceptanceTest extends S3DestinationAcceptanceTest {

  private final JsonAvroConverter converter = new JsonAvroConverter();

  protected S3ParquetDestinationAcceptanceTest() {
    super(S3Format.PARQUET);
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.deserialize("{\n"
        + "  \"format_type\": \"Parquet\",\n"
        + "  \"compression_codec\": \"GZIP\"\n"
        + "}");
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws IOException, URISyntaxException {
    JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
    schemaConverter.getAvroSchema(streamSchema, streamName, namespace, true);
    JsonFieldNameUpdater nameUpdater = new JsonFieldNameUpdater(schemaConverter.getStandardizedNames());

    List<S3ObjectSummary> objectSummaries = getAllSyncedObjects(streamName, namespace);
    List<JsonNode> jsonRecords = new LinkedList<>();

    for (S3ObjectSummary objectSummary : objectSummaries) {
      S3Object object = s3Client.getObject(objectSummary.getBucketName(), objectSummary.getKey());
      URI uri = new URI(String.format("s3a://%s/%s", object.getBucketName(), object.getKey()));
      var path = new org.apache.hadoop.fs.Path(uri);
      Configuration hadoopConfig = S3ParquetWriter.getHadoopConfig(config);
      ParquetReader<GenericData.Record> parquetReader = ParquetReader.<GenericData.Record>builder(new AvroReadSupport<>(), path)
          .withConf(hadoopConfig)
          .build();

      ObjectReader jsonReader = MAPPER.reader();
      GenericData.Record record;
      while ((record = parquetReader.read()) != null) {
        byte[] jsonBytes = converter.convertToJson(record);
        JsonNode jsonRecord = jsonReader.readTree(jsonBytes);
        jsonRecord = nameUpdater.getJsonWithOriginalFieldNames(jsonRecord);
        jsonRecords.add(pruneAirbyteJson(jsonRecord));
      }
    }

    return jsonRecords;
  }

  /**
   * Convert an Airbyte JsonNode from Parquet to a plain one.
   * <li>Remove the airbyte id and emission timestamp fields.</li>
   * <li>Remove null fields that must exist in Parquet but does not in original Json.</li> This
   * function mutates the input Json.
   */
  private static JsonNode pruneAirbyteJson(JsonNode input) {
    ObjectNode output = (ObjectNode) input;

    // Remove Airbyte columns.
    output.remove(JavaBaseConstants.COLUMN_NAME_AB_ID);
    output.remove(JavaBaseConstants.COLUMN_NAME_EMITTED_AT);

    // Fields with null values does not exist in the original Json but only in Parquet.
    for (String field : MoreIterators.toList(output.fieldNames())) {
      if (output.get(field) == null || output.get(field).isNull()) {
        output.remove(field);
      }
    }

    return output;
  }

}
