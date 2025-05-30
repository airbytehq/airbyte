/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations
import io.airbyte.commons.json.Jsons
import java.sql.ResultSet
import java.sql.SQLException
import java.util.Locale

class MysqlTestSourceOperations : JdbcSourceOperations() {
    @Throws(SQLException::class)
    override fun copyToJsonField(resultSet: ResultSet, colIndex: Int, json: ObjectNode) {
        val columnName = resultSet.metaData.getColumnName(colIndex)
        val columnTypeName =
            resultSet.metaData.getColumnTypeName(colIndex).lowercase(Locale.getDefault())

        // JSON has no equivalent in JDBCType
        if ("json" == columnTypeName) {
            json.set<JsonNode>(columnName, Jsons.deserializeExact(resultSet.getString(colIndex)))
        } else {
            super.copyToJsonField(resultSet, colIndex, json)
        }
    }
}
