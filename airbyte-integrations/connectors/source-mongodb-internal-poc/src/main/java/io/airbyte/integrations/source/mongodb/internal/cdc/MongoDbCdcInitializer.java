package io.airbyte.integrations.source.mongodb.internal.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.MongoClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumStateUtil;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Instant;
import java.util.List;
import java.util.OptionalLong;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.REPLICA_SET_CONFIGURATION_KEY;

public class MongoDbCdcInitializer {

    private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbCdcInitializer.class);

    private final MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil;

    public MongoDbCdcInitializer() {
        mongoDbDebeziumStateUtil = new MongoDbDebeziumStateUtil();
    }

    public List<AutoCloseableIterator<AirbyteMessage>> createCdcIterators(
            final MongoClient mongoClient,
            final ConfiguredAirbyteCatalog catalog,
            final MongoDbStateManager stateManager,
            final Instant emittedAt,
            final JsonNode config
            ) {

        final String databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();
        final String replicaSet = config.get(REPLICA_SET_CONFIGURATION_KEY).asText();
        final MongoDbCdcState cdcState = getCdcState(mongoClient, stateManager, databaseName, replicaSet);
        final OptionalLong savedOffset = mongoDbDebeziumStateUtil.savedOffset(MongoDbCdcProperties.getDebeziumProperties(), catalog, Jsons.jsonNode(cdcState), config);

        // We should always be able to extract offset out of state if it's not null
        if (cdcState != null && savedOffset.isEmpty()) {
            throw new RuntimeException(
                    "Unable extract the offset out of state, State mutation might not be working. " + cdcState);
        }

        final boolean savedOffsetAfterResumeToken = mongoDbDebeziumStateUtil.isSavedOffsetAfterResumeToken(mongoClient, savedOffset);

        if (!savedOffsetAfterResumeToken) {
            LOGGER.warn("Saved offset is before most recent resume token. Airbyte will trigger a full refresh.");
        }

        final MongoDbCdcState stateToBeUsed = (!savedOffsetAfterResumeToken || stateManager.getCdcState() == null) ? cdcState : stateManager.getCdcState();
    }

    private MongoDbCdcState getCdcState(final MongoClient mongoClient, final MongoDbStateManager stateManager, final String databaseName, final String replicaSet) {
        final JsonNode initialDebeziumState = mongoDbDebeziumStateUtil.constructInitialDebeziumState(mongoClient, databaseName, replicaSet);
        return (stateManager.getCdcState() == null) ? Jsons.object(initialDebeziumState, MongoDbCdcState.class) : stateManager.getCdcState();
    }
}
