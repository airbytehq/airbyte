/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import java.sql.Connection
import java.sql.SQLException

object RedshiftConnectionHandler {
    /**
     * For to close a connection. Aimed to be use in test only.
     *
     * @param connection The connection to close
     */
    fun close(connection: Connection) {
        try {
            connection.autoCommit = false
            connection.commit()
            connection.close()
        } catch (e: SQLException) {
            throw RuntimeException(e)
        }
    }
}
