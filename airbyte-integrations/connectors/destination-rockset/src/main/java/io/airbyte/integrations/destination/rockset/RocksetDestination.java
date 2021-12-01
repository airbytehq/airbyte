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

package io.airbyte.integrations.destination.rockset;

import static io.airbyte.integrations.destination.rockset.RocksetUtils.WORKSPACE_ID;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import com.rockset.client.ApiClient;
import com.rockset.client.RocksetClient;
import com.rockset.client.api.CollectionsApi;
import com.rockset.client.api.DocumentsApi;
import com.rockset.client.model.AddDocumentsRequest;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;

import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RocksetDestination extends BaseConnector implements Destination {

    private static final Logger LOGGER = LoggerFactory.getLogger(RocksetDestination.class);
    private static final ObjectMapper mapper = new ObjectMapper();

    public static void main(String[] args) throws Exception {
        new IntegrationRunner(new RocksetDestination()).run(args);
    }

    @Override
    public AirbyteConnectionStatus check(final JsonNode config) {
        ApiClient client = null;
        String workspace = null;
        // Create a temporary table
        final String cname = "tmp_test_collection_" + RandomStringUtils.randomAlphabetic(7).toLowerCase();

        try {
            client = RocksetUtils.apiClientFromConfig(config);

            workspace = config.get(WORKSPACE_ID).asText();
            RocksetUtils.createWorkspaceIfNotExists(client, workspace);


            RocksetUtils.createCollectionIfNotExists(client, workspace, cname);
            RocksetUtils.waitUntilCollectionReady(client, workspace, cname);

            // Write a single document
            final String unique = UUID.randomUUID().toString();
            final Map<String, String> dummyRecord = ImmutableMap.of("_id", unique);
            final AddDocumentsRequest req = new AddDocumentsRequest();
            req.addDataItem(mapper.convertValue(dummyRecord, new TypeReference<>() {
            }));
            new DocumentsApi(client).add(workspace, cname, req);

            // Verify that the doc shows up
            final String sql = String.format("SELECT * FROM %s.%s WHERE _id = '%s';", workspace, cname, unique);
            RocksetUtils.waitUntilDocCount(client, sql, 1);

            LOGGER.info("Check succeeded");
            return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
        } catch (Exception e) {
            LOGGER.info("Check failed.", e);
            return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage() != null ? e.getMessage() : e.toString());
        } finally {
            // Delete the collection
            if (client != null && workspace != null) {
                RocksetUtils.deleteCollectionIfExists(client, workspace, cname);
            }

        }
    }

    @Override
    public AirbyteMessageConsumer getConsumer(
            JsonNode config,
            ConfiguredAirbyteCatalog catalog,
            Consumer<AirbyteMessage> outputRecordCollector)
            throws Exception {
        return new RocksetWriteApiConsumer(config, catalog, outputRecordCollector);
    }

}
