package io.airbyte.cdk.source.select

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.TableName

/** Used to determine a high-water mark for a cursor column.  */
class MaxCursorValueQuerier(
    val queryBuilder: SelectQueryGenerator,
    val querier: SelectQuerier,
) {

    fun query(table: TableName, cursor: Field): JsonNode? {
        val querySpec = SelectQuerySpec(SelectColumnMaxValue(cursor), From(table))
        val q: SelectQuery = queryBuilder.generate(querySpec.optimize())
        var maybeRecord: ObjectNode? = null
        querier.executeQuery(q) { record: ObjectNode ->
            maybeRecord = record
            true
        }
        val record: ObjectNode = maybeRecord ?: return null
        val value: JsonNode = record[cursor.id] ?: NullNode.getInstance()
        if (value.isNull) {
            throw IllegalStateException("NULL value found for cursor ${cursor.id}")
        }
        return value
    }
}
