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

package io.airbyte.server;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class ConfigDumpImporterTest {

  @Test
  public void testReplaceDeploymentMetadata() throws Exception {
    final UUID oldDeploymentUuid = UUID.randomUUID();
    final UUID newDeploymentUuid = UUID.randomUUID();

    final JsonNode airbyteVersion = Jsons.deserialize("{\"key\":\"airbyte_version\",\"value\":\"dev\"}");
    final JsonNode serverUuid = Jsons.deserialize("{\"key\":\"server_uuid\",\"value\":\"e895a584-7dbf-48ce-ace6-0bc9ea570c34\"}");
    final JsonNode date = Jsons.deserialize("{\"key\":\"date\",\"value\":\"1956-08-17\"}");
    final JsonNode oldDeploymentId = Jsons.deserialize(
        String.format("{\"key\":\"%s\",\"value\":\"%s\"}", DefaultJobPersistence.DEPLOYMENT_ID_KEY, oldDeploymentUuid));
    final JsonNode newDeploymentId = Jsons.deserialize(
        String.format("{\"key\":\"%s\",\"value\":\"%s\"}", DefaultJobPersistence.DEPLOYMENT_ID_KEY, newDeploymentUuid));

    final JobPersistence jobPersistence = mock(JobPersistence.class);

    // when new deployment id does not exist, the old deployment id is removed
    when(jobPersistence.getDeployment()).thenReturn(Optional.empty());
    final Stream<JsonNode> inputStream1 = Stream.of(airbyteVersion, serverUuid, date, oldDeploymentId);
    final Stream<JsonNode> outputStream1 = ConfigDumpImporter.replaceDeploymentMetadata(jobPersistence, inputStream1);
    final Stream<JsonNode> expectedStream1 = Stream.of(airbyteVersion, serverUuid, date);
    assertEquals(expectedStream1.collect(Collectors.toList()), outputStream1.collect(Collectors.toList()));

    // when new deployment id exists, the old deployment id is replaced with the new one
    when(jobPersistence.getDeployment()).thenReturn(Optional.of(newDeploymentUuid));
    final Stream<JsonNode> inputStream2 = Stream.of(airbyteVersion, serverUuid, date, oldDeploymentId);
    final Stream<JsonNode> outputStream2 = ConfigDumpImporter.replaceDeploymentMetadata(jobPersistence, inputStream2);
    final Stream<JsonNode> expectedStream2 = Stream.of(airbyteVersion, serverUuid, date, newDeploymentId);
    assertEquals(expectedStream2.collect(Collectors.toList()), outputStream2.collect(Collectors.toList()));
  }

}
