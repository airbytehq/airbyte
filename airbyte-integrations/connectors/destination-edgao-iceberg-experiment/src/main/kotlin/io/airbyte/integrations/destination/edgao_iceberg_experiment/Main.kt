package io.airbyte.integrations.destination.edgao_iceberg_experiment

//import aws.sdk.kotlin.runtime.auth.credentials.StaticCredentialsProvider
//import aws.sdk.kotlin.services.glue.GlueClient
//import aws.sdk.kotlin.services.glue.model.Column
//import aws.sdk.kotlin.services.glue.model.CreateDatabaseRequest
//import aws.sdk.kotlin.services.glue.model.CreateTableRequest
//import aws.sdk.kotlin.services.glue.model.UpdateTableRequest
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.time.OffsetDateTime
import java.util.Map
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.aws.glue.GlueCatalog
import org.apache.iceberg.aws.s3.S3FileIOProperties
import org.apache.iceberg.catalog.Namespace
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.parquet.GenericParquetWriter
import org.apache.iceberg.io.DataWriter
import org.apache.iceberg.parquet.Parquet
import org.apache.iceberg.types.Types


private val logger = KotlinLogging.logger {}

fun main(): Unit = runBlocking {
    val glueConfig = Jsons.readTree(File("/Users/edgao/code/airbyte/airbyte-integrations/connectors/destination-edgao-iceberg-experiment/secrets/glue.json"))
    val accessKeyId = glueConfig["storage_config"]["access_key_id"].asText()
    val secretAccessKey = glueConfig["storage_config"]["secret_access_key"].asText()

    val catalog = GlueCatalog()
    catalog.initialize(
        "iceberg",
        mapOf(
            CatalogProperties.CATALOG_IMPL to "org.apache.iceberg.aws.glue.GlueCatalog",
            CatalogProperties.WAREHOUSE_LOCATION to "s3://ab-destination-iceberg/edgao_test_via_iceberg",
            CatalogProperties.FILE_IO_IMPL to "org.apache.iceberg.aws.s3.S3FileIO",
            S3FileIOProperties.ACCESS_KEY_ID to accessKeyId,
            S3FileIOProperties.SECRET_ACCESS_KEY to secretAccessKey,

//            CatalogProperties.CATALOG_IMPL to "org.apache.iceberg.rest.RESTCatalog",
//            CatalogProperties.URI to "http://localhost:8181/",
        ),
    )
    val namespace = Namespace.of("edgao_test_namespace")
    val tableId = TableIdentifier.of("edgao_test_namespace", "edgao_test_table")
    val structType = Types.StructType.of(
        Types.NestedField.required(4, "bar", Types.IntegerType.get()),
    )
    val schema =
        Schema(
            Types.NestedField.required(1, "uuid", Types.StringType.get()),
            Types.NestedField.required(2, "updated_at", Types.TimestampType.withZone()),
            Types.NestedField.required(
                3,
                "foo",
                structType,
            ),
        )
//    catalog.createNamespace(namespaceId)
//    catalog.createTable(tableId, schema)

    val table = catalog.loadTable(tableId)

    val path = table.location() + "/" + System.currentTimeMillis()
    val file = table.io().newOutputFile(path)
    val dataWriter: DataWriter<GenericRecord> =
        Parquet.writeData(file)
            .schema(schema)
            .createWriterFunc(GenericParquetWriter::buildWriter)
            .overwrite()
            .withSpec(PartitionSpec.unpartitioned())
            .build()

    val structRecord: GenericRecord = GenericRecord.create(structType)
    val records = listOf(
        GenericRecord.create(schema).copy(
            mapOf(
                "uuid" to "4f37e94e-741e-40fc-9e3f-f75f5ffacaba",
                "updated_at" to OffsetDateTime.now(),
                "foo" to structRecord.copy(mapOf("bar" to 43)),
            ),
        ),
    )

    dataWriter.use { writer ->
        records.forEach {
            writer.write(it)
        }
    }

    table.newAppend()
        .appendFile(dataWriter.toDataFile())
        .commit()


//    val glueClient = GlueClient {
//        credentialsProvider = StaticCredentialsProvider {
//            this.accessKeyId = accessKeyId
//            this.secretAccessKey = secretAccessKey
//        }
//        region = "us-east-2"
//    }
//    val databaseName = "edgao_test_database"
//    val tableName = "edgao_test_table"
//    // TODO create if not exists, for now just do it manually
//    if (false) {
//        glueClient.createDatabase(
//            CreateDatabaseRequest.invoke {
//                databaseInput {
//                    name = databaseName
//                }
//            },
//        )
//        glueClient.createTable(
//            CreateTableRequest.invoke {
//                this.databaseName = databaseName
//                tableInput {
//                    name = tableName
//                }
//            },
//        )
//    }
//
//    println("${LocalTime.now()} starting update")
//    glueClient.updateTable(UpdateTableRequest.invoke {
//        this.databaseName = databaseName
//        tableInput {
//            name = tableName
//            storageDescriptor {
//                location = "s3://ab-destination-iceberg/edgao_test/test2.jsonl"
//                columns = listOf(
//                    Column.invoke {
//                        name = "uuid"
//                        type = "string"
//                    },
//                    Column.invoke {
//                        name = "updated_at"
//                        type = "timestamp"
//                    },
//                    Column.invoke {
//                        name = "foo"
//                        type = "struct<bar: INT>"
//                    },
//                )
//            }
//        }
//    })
//    println("${LocalTime.now()} done with update")
//    glueClient.close()
//    println("${LocalTime.now()} closed client")
}
