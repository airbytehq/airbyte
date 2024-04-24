/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectReader
import io.airbyte.cdk.integrations.destination.s3.avro.AvroConstants
import io.airbyte.cdk.integrations.destination.s3.parquet.S3ParquetWriter
import io.airbyte.cdk.integrations.destination.s3.util.AvroRecordHelper
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.json.Jsons
import java.io.IOException
import java.net.URI
import java.net.URISyntaxException
import java.util.*
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import org.apache.hadoop.fs.Path
import org.apache.parquet.avro.AvroReadSupport
import org.apache.parquet.hadoop.ParquetReader

abstract class S3BaseParquetDestinationAcceptanceTest protected constructor() :
    S3AvroParquetDestinationAcceptanceTest(FileUploadFormat.PARQUET) {
    override val formatConfig: JsonNode?
        get() =
            Jsons.jsonNode(java.util.Map.of("format_type", "Parquet", "compression_codec", "GZIP"))

    @Throws(IOException::class, URISyntaxException::class)
    override fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        val nameUpdater = AvroRecordHelper.getFieldNameUpdater(streamName, namespace, streamSchema)

        val objectSummaries = getAllSyncedObjects(streamName, namespace)
        val jsonRecords: MutableList<JsonNode> = LinkedList()

        for (objectSummary in objectSummaries) {
            val `object` = s3Client!!.getObject(objectSummary.bucketName, objectSummary.key)
            val uri = URI(String.format("s3a://%s/%s", `object`.bucketName, `object`.key))
            val path = Path(uri)
            val hadoopConfig = S3ParquetWriter.getHadoopConfig(s3DestinationConfig)

            ParquetReader.builder<GenericData.Record>(AvroReadSupport<GenericData.Record>(), path)
                .withConf(hadoopConfig)
                .build()
                .use { parquetReader ->
                    val jsonReader: ObjectReader =
                        S3DestinationAcceptanceTest.Companion.MAPPER.reader()
                    var record: GenericData.Record?
                    while ((parquetReader.read().also { record = it }) != null) {
                        val jsonBytes = AvroConstants.JSON_CONVERTER.convertToJson(record)
                        var jsonRecord = jsonReader.readTree(jsonBytes)
                        jsonRecord = nameUpdater.getJsonWithOriginalFieldNames(jsonRecord)
                        jsonRecords.add(AvroRecordHelper.pruneAirbyteJson(jsonRecord))
                    }
                }
        }

        return jsonRecords
    }

    override fun getTestDataComparator(): TestDataComparator = S3AvroParquetTestDataComparator()

    @Throws(Exception::class)
    override fun retrieveDataTypesFromPersistedFiles(
        streamName: String,
        namespace: String
    ): Map<String, Set<Schema.Type>> {
        val objectSummaries = getAllSyncedObjects(streamName, namespace)
        val resultDataTypes: MutableMap<String, Set<Schema.Type>> = HashMap()

        for (objectSummary in objectSummaries) {
            val `object` = s3Client!!.getObject(objectSummary.bucketName, objectSummary.key)
            val uri = URI(String.format("s3a://%s/%s", `object`.bucketName, `object`.key))
            val path = Path(uri)
            val hadoopConfig = S3ParquetWriter.getHadoopConfig(s3DestinationConfig)

            ParquetReader.builder(AvroReadSupport<GenericData.Record>(), path)
                .withConf(hadoopConfig)
                .build()
                .use { parquetReader ->
                    var record: GenericData.Record?
                    while ((parquetReader.read().also { record = it }) != null) {
                        val actualDataTypes = getTypes(record!!)
                        resultDataTypes.putAll(actualDataTypes)
                    }
                }
        }

        return resultDataTypes
    }
}
