/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectReader
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.avro.AvroConstants
import io.airbyte.cdk.integrations.destination.s3.util.AvroRecordHelper.getFieldNameUpdater
import io.airbyte.cdk.integrations.destination.s3.util.AvroRecordHelper.pruneAirbyteJson
import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.json.Jsons
import java.util.*
import org.apache.avro.Schema
import org.apache.avro.file.DataFileReader
import org.apache.avro.file.SeekableByteArrayInput
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.GenericDatumReader

abstract class GcsBaseAvroDestinationAcceptanceTest :
    GcsAvroParquetDestinationAcceptanceTest(FileUploadFormat.AVRO) {
    override val formatConfig: JsonNode?
        get() =
            Jsons.deserialize(
                """{
  "format_type": "Avro",
  "compression_codec": { "codec": "no compression", "compression_level": 5, "include_checksum": true }
}"""
            )

    override fun getTestDataComparator(): TestDataComparator = GcsAvroTestDataComparator()

    @Throws(Exception::class)
    override fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        val nameUpdater = getFieldNameUpdater(streamName, namespace, streamSchema)

        val objectSummaries = getAllSyncedObjects(streamName, namespace!!)
        val jsonRecords: MutableList<JsonNode> = LinkedList()

        for (objectSummary in objectSummaries) {
            val `object` = s3Client.getObject(objectSummary.bucketName, objectSummary.key)
            DataFileReader<GenericData.Record>(
                    SeekableByteArrayInput(`object`.objectContent.readAllBytes()),
                    GenericDatumReader<GenericData.Record>()
                )
                .use { dataFileReader ->
                    val jsonReader: ObjectReader = MAPPER.reader()
                    while (dataFileReader.hasNext()) {
                        val record = dataFileReader.next()
                        val jsonBytes = AvroConstants.JSON_CONVERTER.convertToJson(record)
                        var jsonRecord = jsonReader.readTree(jsonBytes)
                        jsonRecord = nameUpdater.getJsonWithOriginalFieldNames(jsonRecord!!)
                        jsonRecords.add(pruneAirbyteJson(jsonRecord))
                    }
                }
        }

        return jsonRecords
    }

    @Throws(Exception::class)
    override fun retrieveDataTypesFromPersistedFiles(
        streamName: String,
        namespace: String
    ): Map<String?, Set<Schema.Type?>?> {
        val objectSummaries = getAllSyncedObjects(streamName, namespace)
        val resultDataTypes: MutableMap<String?, Set<Schema.Type?>?> = HashMap()

        for (objectSummary in objectSummaries!!) {
            val `object` = s3Client!!.getObject(objectSummary!!.bucketName, objectSummary.key)
            DataFileReader(
                    SeekableByteArrayInput(`object`.objectContent.readAllBytes()),
                    GenericDatumReader<GenericData.Record>()
                )
                .use { dataFileReader ->
                    while (dataFileReader.hasNext()) {
                        val record = dataFileReader.next()
                        val actualDataTypes = getTypes(record)
                        resultDataTypes.putAll(actualDataTypes!!)
                    }
                }
        }
        return resultDataTypes
    }

    override fun getProtocolVersion() = ProtocolVersion.V1
}
