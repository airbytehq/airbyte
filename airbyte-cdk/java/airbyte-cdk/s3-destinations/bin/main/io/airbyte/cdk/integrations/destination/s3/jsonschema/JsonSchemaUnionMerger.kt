/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.jsonschema

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

class JsonSchemaUnionMerger : JsonSchemaIdentityMapper() {
    /*
       This is a kludge to move "merging unions of objects" upstream
       of the AvroPreprocessor.
    */

    // Merge the right object's properties into the left's, recursively
    private fun mergeRightObjectIntoLeft(left: ObjectNode, right: ObjectNode) {
        val leftProperties = left["properties"] as ObjectNode
        val rightProperties = right["properties"] as ObjectNode
        rightProperties.fields().forEach { (rightPropertyName, rightPropertySchema) ->
            if (!leftProperties.has(rightPropertyName)) {
                // Just add the property if it doesn't exist
                leftProperties.set<ObjectNode>(rightPropertyName, rightPropertySchema as ObjectNode)
            } else {
                // Otherwise recursively merge
                val leftPropertySchema = leftProperties[rightPropertyName] as ObjectNode
                if (leftPropertySchema != rightPropertySchema) {
                    val leftType = AirbyteJsonSchemaType.fromJsonSchema(leftPropertySchema)
                    val rightType =
                        AirbyteJsonSchemaType.fromJsonSchema(rightPropertySchema as ObjectNode)
                    if (
                        leftType == AirbyteJsonSchemaType.OBJECT_WITH_PROPERTIES &&
                            rightType == leftType
                    ) {
                        mergeRightObjectIntoLeft(leftPropertySchema, rightPropertySchema)
                    } else {
                        // Combine the non-matching properties into a union. If they are unions,
                        // merge their options.
                        val leftOptions = AirbyteJsonSchemaType.getOptions(leftPropertySchema)
                        val rightOptions = AirbyteJsonSchemaType.getOptions(rightPropertySchema)
                        val newOptions = MoreMappers.initMapper().createArrayNode()
                        val optionsUnique = mutableSetOf<ObjectNode>()
                        for (option in leftOptions) {
                            optionsUnique.add(option)
                        }
                        for (option in rightOptions) {
                            optionsUnique.add(option)
                        }
                        for (option in optionsUnique) {
                            newOptions.add(option)
                        }
                        val newUnion = MoreMappers.initMapper().createObjectNode()
                        newUnion.replace("oneOf", newOptions)
                        leftProperties.set<ObjectNode>(rightPropertyName, newUnion)
                    }
                } // Do nothing if the properties are the same
            }
        }
    }

    override fun mapUnion(schema: ObjectNode): ObjectNode {
        val newSchema = MoreMappers.initMapper().createObjectNode()
        val newOptions = MoreMappers.initMapper().createArrayNode()

        // Start an empty mergeable object
        val mergedObj = MoreMappers.initMapper().createObjectNode()
        mergedObj.put("type", "object")
        val mergedProperties = MoreMappers.initMapper().createObjectNode()
        mergedObj.replace("properties", mergedProperties)

        val seenSet = mutableSetOf<ObjectNode>()
        val options = schema["oneOf"] ?: schema["anyOf"] ?: schema["allOf"]
        for (oldOption in options) {
            val remappedOldOption = mapSchema(oldOption as ObjectNode)

            // Drop null types from the union.
            if (
                AirbyteJsonSchemaType.fromJsonSchema(remappedOldOption) ==
                    AirbyteJsonSchemaType.NULL
            ) {
                continue
            }

            if (seenSet.contains(remappedOldOption)) {
                continue
            }
            seenSet.add(remappedOldOption)
            if (
                AirbyteJsonSchemaType.fromJsonSchema(remappedOldOption) ==
                    AirbyteJsonSchemaType.OBJECT_WITH_PROPERTIES
            ) {
                mergeRightObjectIntoLeft(mergedObj, remappedOldOption)
            } else {
                newOptions.add(remappedOldOption)
            }
        }

        // Only add the merged object if we added at least one object
        if (mergedProperties.size() > 0) {
            newOptions.add(mergedObj)
        }

        // Special case: only one option remains: this is no longer a union
        if (newOptions.size() == 1) {
            return newOptions[0] as ObjectNode
        } else if (newOptions.size() == 0) {
            // If there are no options, it's because they were all nulls
            // Which probably shouldn't happen.
            val nullSchema = MoreMappers.initMapper().createObjectNode()
            nullSchema.put("type", "null")
            return nullSchema
        }

        newSchema.replace("oneOf", newOptions)

        return newSchema
    }

    override fun mapCombined(schema: ObjectNode): ObjectNode {
        val toUnion = super.mapCombined(schema)
        return mapUnion(toUnion)
    }
}
