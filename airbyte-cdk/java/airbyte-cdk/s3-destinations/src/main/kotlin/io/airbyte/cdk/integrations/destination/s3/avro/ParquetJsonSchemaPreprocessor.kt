package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

class ParquetJsonSchemaPreprocessor : JsonSchemaTransformer() {
    data class Context(
        val disjointRecord: ObjectNode? = null,
        var handlingOption: Boolean = false
    )
    private val stack = mutableListOf<Context>()
    private val handlingOption get() = stack.lastOrNull()?.handlingOption ?: false

    override fun visitStartOfUnion(node: ObjectNode) {
        val airbyteType = MoreMappers.initMapper().createObjectNode()
        airbyteType.put("type", "string")

        val properties = MoreMappers.initMapper().createObjectNode()
        properties.replace("_airbyte_type", airbyteType)

        val disjointRecordNode = MoreMappers.initMapper().createObjectNode()
        disjointRecordNode.put("type", "object")
        disjointRecordNode.replace("properties", properties)

        stack.add(Context(disjointRecordNode))
    }

    override fun visitUnionOption(node: ObjectNode) {
        stack.last().handlingOption = true
    }

    override fun visitEndOfUnion(node: ObjectNode) {
        val oldContext = stack.removeLast()
        add(oldContext.disjointRecord!!)
    }

    private fun handleOptionCommon(typeName: String, schema: ObjectNode? = null) {
        val disjointRecord = stack.last().disjointRecord
        println("Adding $typeName option to union type: $disjointRecord")
        val properties = disjointRecord!!.get("properties")
        if (properties.has(typeName)) {
            throw IllegalStateException("Union type cannot have multiple $typeName options")
        }

        if (schema != null) {
            (properties as ObjectNode).replace(typeName, schema)
        } else {
            val typeObject = MoreMappers.initMapper().createObjectNode()
            typeObject.put("type", typeName)
            (properties as ObjectNode).replace(typeName, typeObject)
        }
        stack.last().handlingOption = false
    }

    override fun visitObjectWithProperties(node: ObjectNode) {
        stack.add(Context())
        super.visitObjectWithProperties(node)
    }

    override fun visitEndOfObjectWithProperties(node: ObjectNode) {
        stack.removeLast()
        super.visitEndOfObjectWithProperties(node)
    }

    override fun visitArrayWithItems(node: ObjectNode) {
        stack.add(Context())
        super.visitArrayWithItems(node)
    }

    override fun visitEndOfArrayWithItems(node: ObjectNode) {
        stack.removeLast()
        super.visitEndOfArrayWithItems(node)
    }

    override fun visitArrayWithSingleItem(node: ObjectNode) {
        stack.add(Context())
        super.visitArrayWithSingleItem(node)
    }

    override fun visitEndOfArrayWithSingleItem(node: ObjectNode) {
        stack.removeLast()
        super.visitEndOfArrayWithSingleItem(node)
    }

    override fun visitObjectWithoutProperties(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("object")
        } else {
            super.visitObjectWithoutProperties(node)
        }
    }

    override fun visitBoolean(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("boolean")
        } else {
            super.visitBoolean(node)
        }
    }

    override fun visitInteger(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("integer")
        } else {
            super.visitInteger(node)
        }
    }

    override fun visitNumber(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("number")
        } else {
            super.visitNumber(node)
        }
    }

    override fun visitString(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("string")
        } else {
            super.visitString(node)
        }
    }

    override fun visitBinaryData(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("binary")
        } else {
            super.visitBinaryData(node)
        }
    }

    override fun addObjectType(schema: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("object", schema)
        } else {
            super.addObjectType(schema)
        }
    }

    override fun addArrayType(schema: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("array", schema)
        } else {
            super.addArrayType(schema)
        }
    }

    override fun visitDate(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("date")
        } else {
            super.visitDate(node)
        }
    }

    override fun visitTimeWithTimezone(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("time_with_timezone")
        } else {
            super.visitTimeWithTimezone(node)
        }
    }

    override fun visitTimeWithoutTimezone(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("time_without_timezone")
        } else {
            super.visitTimeWithoutTimezone(node)
        }
    }

    override fun visitDateTimeWithTimezone(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("timestamp_with_timezone")
        } else {
            super.visitDateTimeWithTimezone(node)
        }
    }

    override fun visitDateTimeWithoutTimezone(node: ObjectNode) {
        if (handlingOption) {
            handleOptionCommon("timestamp_without_timezone")
        } else {
            super.visitDateTimeWithoutTimezone(node)
        }
    }

    override fun accept(schema: ObjectNode): ObjectNode {
        stack.clear()
        return super.accept(schema)
    }
}
