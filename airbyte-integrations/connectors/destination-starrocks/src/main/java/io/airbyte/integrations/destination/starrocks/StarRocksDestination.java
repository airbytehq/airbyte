/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package io.airbyte.integrations.destination.starrocks;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.function.Consumer;

public class StarRocksDestination extends BaseConnector implements Destination {

    private static final Logger LOG = LoggerFactory.getLogger(StarRocksDestination.class);
    private static final StandardNameTransformer NAME_RESOLVER = new StandardNameTransformer();

    private static Connection conn = null;

    public static void main(String[] args) throws Exception {
        new IntegrationRunner(new StarRocksDestination()).run(args);
    }

    @Override
    public AirbyteConnectionStatus check(JsonNode config) {
        try {
            Preconditions.checkNotNull(config);
            conn = SqlUtil.createJDBCConnection(config);
        } catch (final Exception e) {
            return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage(e.getMessage());
        }
        return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    }

    @Override
    public AirbyteMessageConsumer getConsumer(JsonNode config,
                                              ConfiguredAirbyteCatalog configuredCatalog,
                                              Consumer<AirbyteMessage> outputRecordCollector) {

        LOG.info("JsonNode config: \n" + config.toPrettyString());
        try {
            if (conn == null) {
                conn = SqlUtil.createJDBCConnection(config);
            }
        } catch (SQLException | ClassNotFoundException e) {
            e.printStackTrace();
        }

        return StarRocksBufferedConsumerFactory.create(outputRecordCollector, conn, NAME_RESOLVER, config, configuredCatalog);
    }

}
