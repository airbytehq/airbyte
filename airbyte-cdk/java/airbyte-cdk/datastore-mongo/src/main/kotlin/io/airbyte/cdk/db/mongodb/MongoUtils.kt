/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.mongodb

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import com.mongodb.DBRefCodecProvider
import com.mongodb.client.MongoCollection
import io.airbyte.cdk.db.DataTypeUtils.toISO8601StringWithMilliseconds
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.util.MoreIterators
import io.airbyte.protocol.models.CommonField
import io.airbyte.protocol.models.JsonSchemaType
import java.time.Instant
import java.util.*
import java.util.function.Consumer
import org.bson.*
import org.bson.codecs.*
import org.bson.codecs.configuration.CodecRegistries
import org.bson.codecs.jsr310.Jsr310CodecProvider
import org.bson.types.Decimal128
import org.bson.types.ObjectId
import org.bson.types.Symbol
import org.slf4j.Logger
import org.slf4j.LoggerFactory

object MongoUtils {
    private val LOGGER: Logger = LoggerFactory.getLogger(MongoUtils::class.java)

    // Shared constants
    const val MONGODB_SERVER_URL: String = "mongodb://%s%s:%s/%s?authSource=admin&ssl=%s"
    const val MONGODB_CLUSTER_URL: String =
        "mongodb+srv://%s%s/%s?retryWrites=true&w=majority&tls=true"
    const val MONGODB_REPLICA_URL: String =
        "mongodb://%s%s/%s?authSource=admin&directConnection=false&ssl=true"
    const val USER: String = "user"
    const val INSTANCE_TYPE: String = "instance_type"
    const val INSTANCE: String = "instance"
    const val CLUSTER_URL: String = "cluster_url"
    const val SERVER_ADDRESSES: String = "server_addresses"
    const val REPLICA_SET: String = "replica_set"

    // MongodbDestination specific constants
    const val AUTH_TYPE: String = "auth_type"
    const val AUTHORIZATION: String = "authorization"
    const val LOGIN_AND_PASSWORD: String = "login/password"
    const val AIRBYTE_DATA_HASH: String = "_airbyte_data_hash"

    // MongodbSource specific constants
    const val AUTH_SOURCE: String = "auth_source"
    const val PRIMARY_KEY: String = "_id"
    val ALLOWED_CURSOR_TYPES: Set<BsonType> =
        java.util.Set.of(
            BsonType.DOUBLE,
            BsonType.STRING,
            BsonType.DOCUMENT,
            BsonType.OBJECT_ID,
            BsonType.DATE_TIME,
            BsonType.INT32,
            BsonType.TIMESTAMP,
            BsonType.INT64,
            BsonType.DECIMAL128
        )

    private const val MISSING_TYPE = "missing"
    private const val NULL_TYPE = "null"
    const val AIRBYTE_SUFFIX: String = "_aibyte_transform"
    private const val DISCOVER_LIMIT = 10000
    private const val ID = "_id"

    fun getType(dataType: BsonType?): JsonSchemaType {
        return when (dataType) {
            BsonType.BOOLEAN -> JsonSchemaType.BOOLEAN
            BsonType.INT32,
            BsonType.INT64,
            BsonType.DOUBLE,
            BsonType.DECIMAL128 -> JsonSchemaType.NUMBER
            BsonType.STRING,
            BsonType.SYMBOL,
            BsonType.BINARY,
            BsonType.DATE_TIME,
            BsonType.TIMESTAMP,
            BsonType.OBJECT_ID,
            BsonType.REGULAR_EXPRESSION,
            BsonType.JAVASCRIPT -> JsonSchemaType.STRING
            BsonType.ARRAY -> JsonSchemaType.ARRAY
            BsonType.DOCUMENT,
            BsonType.JAVASCRIPT_WITH_SCOPE -> JsonSchemaType.OBJECT
            else -> JsonSchemaType.STRING
        }
    }

    fun toJsonNode(document: Document, columnNames: List<String>): JsonNode {
        val objectNode = Jsons.jsonNode(emptyMap<Any, Any>()) as ObjectNode
        formatDocument(document, objectNode, columnNames)
        return objectNode
    }

    fun getBsonValue(type: BsonType?, value: String): Any {
        try {
            return when (type) {
                BsonType.INT32 -> BsonInt32(value.toInt())
                BsonType.INT64 -> BsonInt64(value.toLong())
                BsonType.DOUBLE -> BsonDouble(value.toDouble())
                BsonType.DECIMAL128 -> Decimal128.parse(value)
                BsonType.TIMESTAMP -> BsonTimestamp(Instant.parse(value).epochSecond.toInt(), 0)
                BsonType.DATE_TIME -> BsonDateTime(Instant.parse(value).toEpochMilli())
                BsonType.OBJECT_ID -> ObjectId(value)
                BsonType.SYMBOL -> Symbol(value)
                BsonType.STRING -> BsonString(value)
                else -> value
            }
        } catch (e: Exception) {
            LOGGER.error(
                String.format("Failed to get BsonValue for field type %s", type),
                e.message
            )
            return value
        }
    }

    fun nodeToCommonField(node: TreeNode<CommonField<BsonType>>): CommonField<BsonType> {
        val field = node.data
        if (node.hasChildren()) {
            val subFields =
                node.children!!
                    .map { obj: TreeNode<CommonField<BsonType>> -> nodeToCommonField(obj) }
                    .toList()
            return CommonField(field.name, field.type, subFields)
        } else {
            return CommonField(field.name, field.type)
        }
    }

    private fun formatDocument(
        document: Document,
        objectNode: ObjectNode,
        columnNames: List<String>
    ) {
        val bsonDocument = toBsonDocument(document)
        try {
            BsonDocumentReader(bsonDocument).use { reader ->
                readDocument(reader, objectNode, columnNames)
            }
        } catch (e: Exception) {
            LOGGER.error("Exception while parsing BsonDocument: {}", e.message)
            throw RuntimeException(e)
        }
    }

    private fun readDocument(
        reader: BsonReader,
        jsonNodes: ObjectNode,
        columnNames: List<String>
    ): ObjectNode {
        reader.readStartDocument()
        while (reader.readBsonType() != BsonType.END_OF_DOCUMENT) {
            val fieldName = reader.readName()
            val fieldType = reader.currentBsonType
            if (BsonType.DOCUMENT == fieldType) {
                // recursion in used to parse inner documents
                jsonNodes.set<JsonNode>(
                    fieldName,
                    readDocument(
                        reader,
                        Jsons.jsonNode(emptyMap<Any, Any>()) as ObjectNode,
                        columnNames
                    )
                )
            } else if (BsonType.ARRAY == fieldType) {
                jsonNodes.set<JsonNode>(fieldName, readArray(reader, columnNames, fieldName))
            } else {
                readField(reader, jsonNodes, columnNames, fieldName, fieldType)
            }
            transformToStringIfMarked(jsonNodes, columnNames, fieldName)
        }
        reader.readEndDocument()

        return jsonNodes
    }

    /** Determines whether TLS/SSL should be enabled for a standalone instance of MongoDB. */
    fun tlsEnabledForStandaloneInstance(config: JsonNode, instanceConfig: JsonNode): Boolean {
        return if (config.has(JdbcUtils.TLS_KEY)) config[JdbcUtils.TLS_KEY].asBoolean()
        else
            (if (instanceConfig.has(JdbcUtils.TLS_KEY))
                instanceConfig[JdbcUtils.TLS_KEY].asBoolean()
            else true)
    }

    fun transformToStringIfMarked(
        jsonNodes: ObjectNode,
        columnNames: List<String>,
        fieldName: String
    ) {
        if (columnNames.contains(fieldName + AIRBYTE_SUFFIX)) {
            val data = jsonNodes[fieldName]
            if (data != null) {
                jsonNodes.remove(fieldName)
                jsonNodes.put(
                    fieldName + AIRBYTE_SUFFIX,
                    if (data.isTextual) data.asText() else data.toString()
                )
            } else {
                LOGGER.debug(
                    "WARNING Field list out of sync, Document doesn't contain field: {}",
                    fieldName
                )
            }
        }
    }

    private fun readArray(
        reader: BsonReader,
        columnNames: List<String>,
        fieldName: String
    ): JsonNode {
        reader.readStartArray()
        val elements = Lists.newArrayList<Any?>()

        while (reader.readBsonType() != BsonType.END_OF_DOCUMENT) {
            val arrayFieldType = reader.currentBsonType
            if (BsonType.DOCUMENT == arrayFieldType) {
                // recursion is used to read inner doc
                elements.add(
                    readDocument(
                        reader,
                        Jsons.jsonNode(emptyMap<Any, Any>()) as ObjectNode,
                        columnNames
                    )
                )
            } else if (BsonType.ARRAY == arrayFieldType) {
                // recursion is used to read inner array
                elements.add(readArray(reader, columnNames, fieldName))
            } else {
                val element =
                    readField(
                        reader,
                        Jsons.jsonNode(emptyMap<Any, Any>()) as ObjectNode,
                        columnNames,
                        fieldName,
                        arrayFieldType
                    )
                elements.add(element[fieldName])
            }
        }
        reader.readEndArray()
        return Jsons.jsonNode(MoreIterators.toList(elements.iterator()))
    }

    private fun readField(
        reader: BsonReader,
        o: ObjectNode,
        columnNames: List<String>,
        fieldName: String,
        fieldType: BsonType
    ): ObjectNode {
        when (fieldType) {
            BsonType.BOOLEAN -> o.put(fieldName, reader.readBoolean())
            BsonType.INT32 -> o.put(fieldName, reader.readInt32())
            BsonType.INT64 -> o.put(fieldName, reader.readInt64())
            BsonType.DOUBLE -> o.put(fieldName, reader.readDouble())
            BsonType.DECIMAL128 -> o.put(fieldName, toDouble(reader.readDecimal128()))
            BsonType.TIMESTAMP ->
                o.put(fieldName, toISO8601StringWithMilliseconds(reader.readTimestamp().value))
            BsonType.DATE_TIME ->
                o.put(fieldName, toISO8601StringWithMilliseconds(reader.readDateTime()))
            BsonType.BINARY -> o.put(fieldName, toByteArray(reader.readBinaryData()))
            BsonType.SYMBOL -> o.put(fieldName, reader.readSymbol())
            BsonType.STRING -> o.put(fieldName, reader.readString())
            BsonType.OBJECT_ID -> o.put(fieldName, toString(reader.readObjectId()))
            BsonType.JAVASCRIPT -> o.put(fieldName, reader.readJavaScript())
            BsonType.JAVASCRIPT_WITH_SCOPE ->
                readJavaScriptWithScope(o, reader, fieldName, columnNames)
            BsonType.REGULAR_EXPRESSION -> toString(reader.readRegularExpression())
            else -> reader.skipValue()
        }
        return o
    }

    /**
     * Gets 10.000 documents from collection, gathers all unique fields and its type. In case when
     * one field has different types in 2 and more documents, the type is set to String.
     *
     * @param collection mongo collection
     * @return map of unique fields and its type
     */
    fun getUniqueFields(
        collection: MongoCollection<Document>
    ): List<TreeNode<CommonField<BsonType>>> {
        val allkeys = HashSet(getFieldsName(collection))

        return allkeys
            .map { key: String ->
                val types = getTypes(collection, key)
                val type = getUniqueType(types)
                val fieldNode = TreeNode(CommonField(transformName(types, key), type))
                if (type == BsonType.DOCUMENT) {
                    setSubFields(collection, fieldNode, key)
                }
                fieldNode
            }
            .toList()
    }

    /**
     * If one field has different types in 2 and more documents, the name is transformed to
     * 'name_aibyte_transform'.
     *
     * @param types list with field types
     * @param name field name
     * @return name
     */
    private fun transformName(types: List<String>, name: String): String {
        return if (types.size != 1) name + AIRBYTE_SUFFIX else name
    }

    private fun setSubFields(
        collection: MongoCollection<Document>,
        parentNode: TreeNode<CommonField<BsonType>>?,
        pathToField: String
    ) {
        val nestedKeys = getFieldsName(collection, pathToField)
        nestedKeys!!.forEach(
            Consumer { key: String ->
                val types = getTypes(collection, "$pathToField.$key")
                val nestedType = getUniqueType(types)
                val childNode =
                    parentNode!!.addChild(CommonField(transformName(types, key), nestedType))
                if (nestedType == BsonType.DOCUMENT) {
                    setSubFields(collection, childNode, "$pathToField.$key")
                }
            }
        )
    }

    private fun getFieldsName(collection: MongoCollection<Document>): List<String>? {
        return getFieldsName(collection, "\$ROOT")
    }

    private fun getFieldsName(
        collection: MongoCollection<Document>,
        fieldName: String
    ): List<String>? {
        val output =
            collection.aggregate(
                Arrays.asList(
                    Document("\$limit", DISCOVER_LIMIT),
                    Document(
                        "\$project",
                        Document("arrayofkeyvalue", Document("\$objectToArray", "$$fieldName"))
                    ),
                    Document("\$unwind", "\$arrayofkeyvalue"),
                    Document(
                        "\$group",
                        Document(ID, null)
                            .append("allkeys", Document("\$addToSet", "\$arrayofkeyvalue.k"))
                    )
                )
            )
        return if (output.cursor().hasNext()) {
            @Suppress("unchecked_cast")
            output.cursor().next()["allkeys"] as List<String>?
        } else {
            emptyList()
        }
    }

    private fun getTypes(collection: MongoCollection<Document>, name: String): List<String> {
        val fieldName = "$$name"
        val output =
            collection.aggregate(
                Arrays.asList(
                    Document("\$limit", DISCOVER_LIMIT),
                    Document(
                        "\$project",
                        Document(ID, 0).append("fieldType", Document("\$type", fieldName))
                    ),
                    Document(
                        "\$group",
                        Document(ID, Document("fieldType", "\$fieldType"))
                            .append("count", Document("\$sum", 1))
                    )
                )
            )
        val listOfTypes = ArrayList<String>()
        val cursor = output.cursor()
        while (cursor.hasNext()) {
            val type = (cursor.next()[ID] as Document?)!!["fieldType"].toString()
            if (MISSING_TYPE != type && NULL_TYPE != type) {
                listOfTypes.add(type)
            }
        }
        if (listOfTypes.isEmpty()) {
            listOfTypes.add(NULL_TYPE)
        }
        return listOfTypes
    }

    private fun getUniqueType(types: List<String>): BsonType {
        if (types.size != 1) {
            return BsonType.STRING
        } else {
            val type = types[0]
            return getBsonTypeByTypeAlias(type)
        }
    }

    private fun getBsonTypeByTypeAlias(typeAlias: String): BsonType {
        return when (typeAlias) {
            "object" -> BsonType.DOCUMENT
            "double" -> BsonType.DOUBLE
            "string" -> BsonType.STRING
            "objectId" -> BsonType.OBJECT_ID
            "array" -> BsonType.ARRAY
            "binData" -> BsonType.BINARY
            "bool" -> BsonType.BOOLEAN
            "date" -> BsonType.DATE_TIME
            "null" -> BsonType.NULL
            "regex" -> BsonType.REGULAR_EXPRESSION
            "dbPointer" -> BsonType.DB_POINTER
            "javascript" -> BsonType.JAVASCRIPT
            "symbol" -> BsonType.SYMBOL
            "javascriptWithScope" -> BsonType.JAVASCRIPT_WITH_SCOPE
            "int" -> BsonType.INT32
            "timestamp" -> BsonType.TIMESTAMP
            "long" -> BsonType.INT64
            "decimal" -> BsonType.DECIMAL128
            else -> BsonType.STRING
        }
    }

    private fun toBsonDocument(document: Document): BsonDocument {
        try {
            val customCodecRegistry =
                CodecRegistries.fromProviders(
                    Arrays.asList(
                        ValueCodecProvider(),
                        BsonValueCodecProvider(),
                        DocumentCodecProvider(),
                        IterableCodecProvider(),
                        MapCodecProvider(),
                        Jsr310CodecProvider(),
                        JsonObjectCodecProvider(),
                        BsonCodecProvider(),
                        DBRefCodecProvider()
                    )
                )

            // Override the default codec registry
            return document.toBsonDocument(BsonDocument::class.java, customCodecRegistry)
        } catch (e: Exception) {
            LOGGER.error("Exception while converting Document to BsonDocument: {}", e.message)
            throw RuntimeException(e)
        }
    }

    private fun toString(value: Any?): String? {
        return value?.toString()
    }

    private fun toDouble(value: Decimal128?): Double? {
        return value?.toDouble()
    }

    private fun toByteArray(value: BsonBinary?): ByteArray? {
        return value?.data
    }

    private fun readJavaScriptWithScope(
        o: ObjectNode,
        reader: BsonReader,
        fieldName: String,
        columnNames: List<String>
    ) {
        val code = reader.readJavaScriptWithScope()
        val scope =
            readDocument(reader, Jsons.jsonNode(emptyMap<Any, Any>()) as ObjectNode, columnNames)
        o.set<JsonNode>(fieldName, Jsons.jsonNode(ImmutableMap.of("code", code, "scope", scope)))
    }

    enum class MongoInstanceType(val type: String) {
        STANDALONE("standalone"),
        REPLICA("replica"),
        ATLAS("atlas");

        companion object {
            fun fromValue(value: String): MongoInstanceType {
                for (instance in entries) {
                    if (value.equals(instance.type, ignoreCase = true)) {
                        return instance
                    }
                }
                throw IllegalArgumentException("Unknown instance type value: $value")
            }
        }
    }
}
