/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

class MergeUnions : AirbyteSchemaIdentityMapper {
    override fun mapUnion(schema: UnionType): AirbyteType {
        // Map the options first so they're in their final form
        val mappedOptions = schema.options.map { map(it) }
        val mergedOptions = mergeOptions(mappedOptions)
        return UnionType.of(mergedOptions)
    }

    private fun mergeOptions(options: Iterable<AirbyteType>): Set<AirbyteType> {
        val mergedOptions = mutableSetOf<AirbyteType>()
        mergeOptions(mergedOptions, options)
        return mergedOptions
    }

    private fun mergeOptions(into: MutableSet<AirbyteType>, from: Iterable<AirbyteType>) {
        for (option in from) {
            if (option is UnionType) {
                // If this is a union of a union, recursively merge the other union's options in
                mergeOptions(into, option.options)
            } else if (option is ObjectType) {
                val existingObjOption: ObjectType? = into.find { it is ObjectType } as ObjectType?
                if (existingObjOption == null) {
                    // No other object in the set, so just add this one
                    into.add(option)
                    continue
                }

                into.remove(existingObjOption)
                val newProperties = existingObjOption.properties
                for ((name, field) in option.properties) {
                    val existingField = newProperties[name]
                    newProperties[name] = field
                    if (existingField == null) {
                        // If no field exists with the same name, just adding this one is fine
                        continue
                    }

                    // Combine the fields, recursively merging unions, object fields, etc
                    val mergedFields = map(UnionType.of(existingField.type, field.type))
                    newProperties[name] =
                        FieldType(mergedFields, existingField.nullable || field.nullable)

                    // If the fields are identical, we can just keep the existing field
                }
                into.add(ObjectType(newProperties))
            } else {
                into.add(option)
            }
        }
    }
}
