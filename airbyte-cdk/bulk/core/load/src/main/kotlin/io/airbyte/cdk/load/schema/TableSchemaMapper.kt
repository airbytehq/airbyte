package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.schema.model.TableName

interface TableSchemaMapper {

    fun toFinalTableName(desc: DestinationStream.Descriptor): TableName

    fun toTempTableName(tableName: TableName): TableName

    fun toColumnName(name: String): String

    fun toColumnType(fieldType: FieldType): ColumnType

}
