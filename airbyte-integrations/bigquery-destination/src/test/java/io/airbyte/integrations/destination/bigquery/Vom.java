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

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FormatOptions;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo.CreateDisposition;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.WriteChannelConfiguration;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.singer.SingerMessage;
import io.airbyte.singer.SingerMessage.Type;
import java.io.ByteArrayInputStream;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;

public class Vom {

  private static final Path CREDENTIALS_PATH = Path
      .of("/Users/charles/code/airbyte/airbyte-integrations/bigquery-destination/config/bq_credentials.json");

  private static final SingerMessage SINGER_MESSAGE_TASKS1 = new SingerMessage().withType(Type.RECORD).withStream("tasks")
      .withRecord(new ObjectMapper().createObjectNode().put("goal", "announce the game."));
  private static final SingerMessage SINGER_MESSAGE_TASKS2 = new SingerMessage().withType(Type.RECORD).withStream("tasks")
      .withRecord(new ObjectMapper().createObjectNode().put("goal", "ship some code."));

  public static void main(String[] args) throws Exception {
    String datasetId = "airbyte_tests_4jdpxsy9";

    JsonNode credentialsJson = Jsons.deserialize(IOs.readFile(CREDENTIALS_PATH));
    String credentialsJsonString = new String(Files.readAllBytes(CREDENTIALS_PATH));

    final String projectId = credentialsJson.get("project_id").asText();
    final ServiceAccountCredentials credentials = ServiceAccountCredentials.fromStream(new ByteArrayInputStream(credentialsJsonString.getBytes()));
    BigQuery bigquery = BigQueryOptions.newBuilder()
        .setProjectId(projectId)
        .setCredentials(credentials)
        .build()
        .getService();

    // https://cloud.google.com/bigquery/docs/loading-data-local#loading_data_from_a_local_data_source
    final WriteChannelConfiguration writeChannelConfiguration = WriteChannelConfiguration
        .newBuilder(TableId.of(datasetId, "tasks"))
        .setCreateDisposition(CreateDisposition.CREATE_IF_NEEDED)
        .setSchema(com.google.cloud.bigquery.Schema.of(Field.of("data", StandardSQLTypeName.STRING)))
        .setFormatOptions(FormatOptions.json()).build(); // new line delimited json.

    final TableDataWriteChannel writer = bigquery.writer(JobId.of(UUID.randomUUID().toString()), writeChannelConfiguration);
    final JsonNode data = Jsons.jsonNode(ImmutableMap.of("data", Jsons.serialize(SINGER_MESSAGE_TASKS1.getRecord())));
    final JsonNode data2 = Jsons.jsonNode(ImmutableMap.of("data", Jsons.serialize(SINGER_MESSAGE_TASKS2.getRecord())));
    System.out.println("data = " + data);
    System.out.println("Jsons.serialize(data) = " + Jsons.serialize(data));
    System.out.println("Jsons.serialize(data) = " + Jsons.serialize(data2));
    writer.write(ByteBuffer.wrap((Jsons.serialize(data) + "\n").getBytes(Charsets.UTF_8)));
    writer.write(ByteBuffer.wrap((Jsons.serialize(data2) + "\n").getBytes(Charsets.UTF_8)));

    writer.close();
    writer.getJob().waitFor();
  }

}
