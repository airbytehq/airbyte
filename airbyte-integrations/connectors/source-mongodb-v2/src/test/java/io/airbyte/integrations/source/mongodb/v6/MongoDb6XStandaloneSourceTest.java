package io.airbyte.integrations.source.mongodb.v6;

import io.airbyte.integrations.source.mongodb.AbstractMongoDbStandaloneSourceTest;
import io.airbyte.integrations.source.mongodb.MongoDbVersions;

class MongoDb6XStandaloneSourceTest extends AbstractMongoDbStandaloneSourceTest {

    private static final String COLLECTION_NAME = "movies";
    private static final String CURSOR_FIELD = "index";
    private static final String DB_NAME = "mongo6";
    private static final Integer DATASET_SIZE = 10000;
    private static final Integer LISTEN_PORT = 27006;

    @Override
    protected String getCollectionName() {
        return COLLECTION_NAME;
    }

    @Override
    protected String getCursorField() { return CURSOR_FIELD; }

    @Override
    protected Integer getDataSetSize() {
        return DATASET_SIZE;
    }

    @Override
    protected String getDatabaseName() {
        return DB_NAME;
    }

    @Override
    protected String getMongoDbVersion() { return MongoDbVersions.VERSION_6.getVersion(); }

    @Override
    protected Integer getListenPort() { return LISTEN_PORT; }
}
