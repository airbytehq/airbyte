/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.mongodb

class MongoDatabaseException(databaseName: String?) :
    RuntimeException(String.format(MONGO_DATA_BASE_NOT_FOUND, databaseName)) {
    companion object {
        const val MONGO_DATA_BASE_NOT_FOUND: String = "Data Base with given name - %s not found."
    }
}
