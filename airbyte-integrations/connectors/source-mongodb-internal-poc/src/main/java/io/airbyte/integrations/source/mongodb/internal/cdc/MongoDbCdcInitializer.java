package io.airbyte.integrations.source.mongodb.internal.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.MongoClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.debezium.CdcSavedInfoFetcher;
import io.airbyte.integrations.debezium.CdcStateHandler;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbCdcTargetPosition;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumStateUtil;
import io.airbyte.integrations.debezium.internals.postgres.PostgresCdcTargetPosition;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import org.bson.BsonTimestamp;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.OptionalInt;
import java.util.OptionalLong;
import java.util.Properties;
import java.util.function.Supplier;

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

        final Properties defaultDebeziumProperties = MongoDbCdcProperties.getDebeziumDefaultProperties();
        final String databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();
        final String replicaSet = config.get(REPLICA_SET_CONFIGURATION_KEY).asText();
        final JsonNode initialDebeziumState = mongoDbDebeziumStateUtil.constructInitialDebeziumState(mongoClient, databaseName, replicaSet);
        final JsonNode cdcState = (stateManager.getCdcState() == null || stateManager.getCdcState().state() == null) ? initialDebeziumState :
                Jsons.clone(stateManager.getCdcState().state());
        final OptionalLong savedOffset = mongoDbDebeziumStateUtil.savedOffset(
                Jsons.clone(defaultDebeziumProperties),
                catalog,
                cdcState,
                config
        );

        // We should always be able to extract offset out of state if it's not null
        if (cdcState != null && savedOffset.isEmpty()) {
            throw new RuntimeException(
                    "Unable extract the offset out of state, State mutation might not be working. " + cdcState);
        }

        final boolean savedOffsetAfterResumeToken = mongoDbDebeziumStateUtil.isSavedOffsetAfterResumeToken(mongoClient, savedOffset);

        if (!savedOffsetAfterResumeToken) {
            LOGGER.warn("Saved offset is before most recent resume token. Airbyte will trigger a full refresh.");
        }

        final MongoDbCdcState stateToBeUsed = (!savedOffsetAfterResumeToken || stateManager.getCdcState() == null || stateManager.getCdcState().state() == null) ? new MongoDbCdcState(initialDebeziumState) : stateManager.getCdcState();

        // TODO get iterators for streams

        final Duration firstRecordWaitTime = Duration.ofMinutes(5); // TODO get from connector config?
        final OptionalInt queueSize = OptionalInt.empty(); // TODO get from connector config?
        final AirbyteDebeziumHandler<BsonTimestamp> handler = new AirbyteDebeziumHandler<>(config,
                MongoDbCdcTargetPosition.targetPosition(mongoClient), false, firstRecordWaitTime, queueSize);
        final MongoDbCdcStateHandler mongoDbCdcStateHandler = new MongoDbCdcStateHandler(stateManager);
        final MongoDbCdcConnectorMetadataInjector cdcMetadataInjector = new MongoDbCdcConnectorMetadataInjector();
        final MongoDbCdcSavedInfoFetcher cdcSavedInfoFetcher = new MongoDbCdcSavedInfoFetcher(stateToBeUsed);

        final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(catalog,
                cdcSavedInfoFetcher,
                mongoDbCdcStateHandler,
                cdcMetadataInjector,
                defaultDebeziumProperties,
                emittedAt,
                false);


        return null;
    }

    private MongoDbCdcState getCdcState(final MongoClient mongoClient, final MongoDbStateManager stateManager, final String databaseName, final String replicaSet) {
        if (stateManager.getCdcState() != null) {
            return stateManager.getCdcState();
        } else {
            final JsonNode initialDebeziumState = mongoDbDebeziumStateUtil.constructInitialDebeziumState(mongoClient, databaseName, replicaSet);
            return Jsons.object(initialDebeziumState, MongoDbCdcState.class);
        }
    }
}
