/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.spark

import com.amazonaws.auth.AWSCredentialsProvider
import com.amazonaws.services.s3.AmazonS3
import io.airbyte.cdk.load.command.AvroOutputFormatConfiguration
import io.airbyte.cdk.load.command.CSVOutputFormatConfiguration
import io.airbyte.cdk.load.command.JsonOutputFormatConfiguration
import io.airbyte.cdk.load.command.OutputFormatConfiguration
import io.airbyte.cdk.load.command.ParquetOutputFormatConfiguration
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteTypeToSparkSchema
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueToSparkRow
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.Deserializer
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.RemoteObject
import io.airbyte.cdk.load.message.StagedLocalFile
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.Serializable
import java.nio.file.Path
import org.apache.spark.api.java.function.MapFunction
import org.apache.spark.sql.Encoders
import org.apache.spark.sql.SaveMode
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types.StructType

@Singleton
@Secondary
class DestinationSparkSession {
    val sparkSession: SparkSession =
        SparkSession.builder()
            .appName("Airbyte Spark Writer")
            .config("spark.master", "local")
            .getOrCreate()

    fun withAWSCredentials(
        awsCredentialsProvider: AWSCredentialsProvider
    ): DestinationSparkSession {
        sparkSession
            .conf()
            .set("fs.s3a.access.key", awsCredentialsProvider.credentials.awsAccessKeyId)
        sparkSession
            .conf()
            .set("fs.s3a.secret.key", awsCredentialsProvider.credentials.awsSecretKey)

        return this
    }
}

interface SparkWriter<T : RemoteObject> {
    fun write(
        schema: AirbyteType,
        localFile: StagedLocalFile,
        storagePath: Path,
        fileFormat: OutputFormatConfiguration,
        recordMapper: (AirbyteValue) -> AirbyteValue = { it }
    ): T
}

interface SparkS3WriterFactory {
    fun create(
        s3Client: S3Client,
    ): SparkS3Writer
}

@Singleton
@Secondary
class DefaultSparkS3WriterFactory(
    private val sparkSession: DestinationSparkSession,
    private val deserializer: Deserializer<DestinationMessage>,
) : SparkS3WriterFactory {
    override fun create(
        s3Client: S3Client,
    ): SparkS3Writer {
        return DefaultSparkS3Writer(
            sparkSession.withAWSCredentials(s3Client.credentials).sparkSession,
            s3Client,
            deserializer
        )
    }
}

interface SparkS3Writer : SparkWriter<S3Object>

data class S3Object(
    val bucketName: String,
    override val key: String,
    override val state: Batch.State = Batch.State.PERSISTED,
) : RemoteObject

class SparkS3WriterInner : Serializable {
    companion object {
        fun write(
            sparkSession: SparkSession,
            sourcePath: String,
            destPath: String,
            format: OutputFormatConfiguration,
            schema: StructType,
            deserializer: Deserializer<DestinationMessage>,
            recordMapper: (AirbyteValue) -> AirbyteValue
        ) {
            val dataFrameWriter =
                sparkSession
                    .read()
                    .textFile(sourcePath)
                    .coalesce(1)
                    .map(
                        MapFunction {
                            val record = deserializer.deserialize(it) as DestinationRecord
                            val remapped = recordMapper(record.data)
                            AirbyteValueToSparkRow().convert(remapped)
                        },
                        Encoders.row(schema)
                    )
                    .write()
                    .mode(SaveMode.Overwrite)
            when (format) {
                is JsonOutputFormatConfiguration -> dataFrameWriter.json(destPath)
                is CSVOutputFormatConfiguration -> dataFrameWriter.csv(destPath)
                is AvroOutputFormatConfiguration -> dataFrameWriter.format("avro").save(destPath)
                is ParquetOutputFormatConfiguration -> dataFrameWriter.parquet(destPath)
            }
        }
    }
}

class DefaultSparkS3Writer(
    private val sparkSession: SparkSession,
    private val s3Client: S3Client,
    private val deserializer: Deserializer<DestinationMessage>,
) : SparkS3Writer {
    val log = KotlinLogging.logger {}

    override fun write(
        schema: AirbyteType,
        localFile: StagedLocalFile,
        storagePath: Path,
        fileFormat: OutputFormatConfiguration,
        recordMapper: (AirbyteValue) -> AirbyteValue
    ): S3Object {
        val bucketName = s3Client.bucketName
        val path = "s3a://$bucketName/$storagePath"
        val sparkSchema = AirbyteTypeToSparkSchema().convert(schema)

        log.info { "Streaming file from ${localFile.localFile.path} to $path" }

        SparkS3WriterInner.write(
            sparkSession,
            localFile.localFile.path.toString(),
            path,
            fileFormat,
            sparkSchema,
            deserializer,
            recordMapper
        )

        val objects = s3Client.list(storagePath)
        if (objects.size != 2) {
            throw IllegalStateException(
                "Expected exactly one object to be written to $path, but found $objects"
            )
        }
        val successTag = objects.filter { it.key.endsWith("_SUCCESS") }
        if (successTag.size != 1) {
            throw IllegalStateException(
                "Expected exactly one _SUCCESS tag to be written to $path, but found $successTag"
            )
        }
        log.info { "Deleting _SUCCESS tag: ${successTag.first()}" }
        s3Client.delete(successTag.first())
        log.info { "Yielding new remote file: ${objects.first()}" }
        return objects.first { !it.key.endsWith("_SUCCESS") }
    }
}

class S3Client(
    private val amazonS3: AmazonS3,
    val bucketName: String,
    val credentials: AWSCredentialsProvider,
) {
    fun move(s3Object: S3Object, toPath: Path): S3Object {
        amazonS3.copyObject(bucketName, s3Object.key, bucketName, toPath.toString())
        amazonS3.deleteObject(bucketName, s3Object.key)
        return s3Object.copy(key = toPath.toString())
    }

    fun list(prefix: Path): List<S3Object> {
        return amazonS3.listObjects(bucketName, prefix.toString()).objectSummaries.map {
            S3Object(bucketName, it.key)
        }
    }

    fun delete(s3Object: S3Object) {
        amazonS3.deleteObject(bucketName, s3Object.key)
    }
}
