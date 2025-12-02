/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import java.util.LinkedHashMap

/**
 * A data dumper that reverse-maps sanitized BigLake column names back to their original names.
 *
 * BigLake requires column names to be sanitized (alphanumeric + underscore only), but the test
 * framework expects the original field names from the source schema. This dumper:
 * 1. Uses IcebergDataDumper to read data from the table (with sanitized names)
 * 2. Attempts to reverse-map sanitized names back to originals using the stream schema
 * 3. Returns records with original field names for test validation
 */
class BigLakeDataDumper(
    private val delegateDataDumper: DestinationDataDumper,
) : DestinationDataDumper {

    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val records = delegateDataDumper.dumpRecords(spec, stream)

        // Build a reverse mapping: sanitized name -> original name
        val reverseMapping = buildReverseMapping(stream)

        // Transform each record's field names back to originals
        return records.map { record ->
            record.copy(data = reverseMapFieldNames(record.data, reverseMapping))
        }
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        return delegateDataDumper.dumpFile(spec, stream)
    }

    /**
     * Builds a mapping from sanitized column names to their original names. This allows us to
     * reverse the transformation when reading data.
     */
    private fun buildReverseMapping(stream: DestinationStream): Map<String, String> {
        val mapping = mutableMapOf<String, String>()

        val schema = stream.schema as? ObjectType ?: return mapping

        schema.properties.keys.forEach { originalName ->
            val sanitized = Transformations.toAlphanumericAndUnderscore(originalName)
            mapping[sanitized] = originalName
        }

        return mapping
    }

    /** Recursively reverse-maps field names in an ObjectValue from sanitized to original names. */
    private fun reverseMapFieldNames(
        obj: ObjectValue,
        reverseMapping: Map<String, String>
    ): ObjectValue {
        val remappedValues = LinkedHashMap<String, io.airbyte.cdk.load.data.AirbyteValue>()

        obj.values.forEach { (sanitizedName, value) ->
            // Get the original name, or keep sanitized if not found
            val originalName = reverseMapping[sanitizedName] ?: sanitizedName

            // Recursively handle nested objects
            val remappedValue =
                if (value is ObjectValue) {
                    reverseMapFieldNames(value, reverseMapping)
                } else {
                    value
                }

            remappedValues[originalName] = remappedValue
        }

        return ObjectValue(remappedValues)
    }
}
