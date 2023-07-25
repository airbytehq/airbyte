package io.airbyte.integrations.source.mongodb.v6;

import io.airbyte.integrations.source.mongodb.AbstractMongoDbReplicaSetSourceTest;
import io.airbyte.integrations.source.mongodb.MongoDbVersions;

import java.util.List;

class MongoDb6xReplicaSetSourceTest extends AbstractMongoDbReplicaSetSourceTest {

    private static final String COLLECTION_NAME = "movies";
    private static final String CURSOR_FIELD = "catalogId";
    private static final String DATABASE_NAME = "mongo6";
    private static final Integer DATASET_SIZE = 10000;
    private static final List<Integer> PORT_BINDINGS = List.of(27617, 27618, 27619);

    @Override
    protected String getCollectionName() {
        return COLLECTION_NAME;
    }

    @Override
    protected String getCursorField() { return CURSOR_FIELD; }

    @Override
    protected String getDatabaseName() {
        return DATABASE_NAME;
    }

    @Override
    protected Integer getDataSetSize() {
        return DATASET_SIZE;
    }

    @Override
    protected String getMongoCommand() {
        return "mongosh";
    }

    @Override
    protected String getMongoDbVersion() {
        return MongoDbVersions.VERSION_6.getVersion();
    }

    @Override
    protected List<Integer> getPortBindings() { return PORT_BINDINGS; }
}
