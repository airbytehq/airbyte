/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import com.fasterxml.jackson.databind.JsonNode

/**
 * A wrapper around the instantiated [javax.sql.DataSource].
 *
 * Note that this class does not implement [AutoCloseable]/[java.io.Closeable], as it is not the
 * responsibility of this class to close the provided [javax.sql.DataSource]. This is to avoid
 * accidentally closing a shared resource.
 */
open class AbstractDatabase {
    var sourceConfig: JsonNode? = null
    var databaseConfig: JsonNode? = null
}
