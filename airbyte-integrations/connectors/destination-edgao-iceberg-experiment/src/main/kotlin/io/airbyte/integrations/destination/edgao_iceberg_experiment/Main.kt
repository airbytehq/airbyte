package io.airbyte.integrations.destination.edgao_iceberg_experiment

import aws.sdk.kotlin.runtime.auth.credentials.StaticCredentialsProvider
import aws.sdk.kotlin.services.glue.GlueClient
import aws.sdk.kotlin.services.glue.model.Column
import aws.sdk.kotlin.services.glue.model.CreateDatabaseRequest
import aws.sdk.kotlin.services.glue.model.CreateTableRequest
import aws.sdk.kotlin.services.glue.model.UpdateTableRequest
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.time.LocalTime
import kotlinx.coroutines.runBlocking

private val logger = KotlinLogging.logger {}

fun main(): Unit = runBlocking {
    val glueConfig = Jsons.readTree(File("/Users/edgao/code/airbyte/airbyte-integrations/connectors/destination-edgao-iceberg-experiment/secrets/glue.json"))
    val accessKeyId = glueConfig["storage_config"]["access_key_id"].asText()
    val secretAccessKey = glueConfig["storage_config"]["secret_access_key"].asText()
//    S3FileIOProperties.SECRET_ACCESS_KEY

//    val catalog = GlueCatalog()
////    val conf = Configuration()
////    catalog.setConf(Configuration())
//    catalog.initialize(
//        "iceberg",
//        mapOf(
////            CatalogProperties.CATALOG_IMPL to "org.apache.iceberg.aws.glue.GlueCatalog",
////            CatalogProperties.WAREHOUSE_LOCATION to "s3://ab-destination-iceberg/demo",
////            CatalogProperties.FILE_IO_IMPL to "org.apache.iceberg.aws.s3.S3FileIO",
////            S3FileIOProperties.ACCESS_KEY_ID to accessKeyId,
////            S3FileIOProperties.SECRET_ACCESS_KEY to secretAccessKey,
//
//            CatalogProperties.CATALOG_IMPL to "org.apache.iceberg.rest.RESTCatalog",
//            CatalogProperties.URI to "http://localhost:8181/",
//        )
//    )
//    // software.amazon.awssdk.services.glue.model.AlreadyExistsException
//    catalog.createNamespace(Namespace.of("edgao_test"))


    val glueClient = GlueClient {
        credentialsProvider = StaticCredentialsProvider {
            this.accessKeyId = accessKeyId
            this.secretAccessKey = secretAccessKey
        }
        region = "us-east-2"
    }
    val databaseName = "edgao_test_database"
    val tableName = "edgao_test_table"
    // TODO create if not exists, for now just do it manually
    if (false) {
        glueClient.createDatabase(
            CreateDatabaseRequest.invoke {
                databaseInput {
                    name = databaseName
                }
            },
        )
        glueClient.createTable(
            CreateTableRequest.invoke {
                this.databaseName = databaseName
                tableInput {
                    name = tableName
                }
            },
        )
    }

    println("${LocalTime.now()} starting update")
    glueClient.updateTable(UpdateTableRequest.invoke {
        this.databaseName = databaseName
        tableInput {
            name = tableName
            storageDescriptor {
                location = "s3://ab-destination-iceberg/edgao_test/test2.jsonl"
                columns = listOf(
                    Column.invoke {
                        name = "uuid"
                        type = "string"
                    },
                    Column.invoke {
                        name = "updated_at"
                        type = "timestamp"
                    },
                    Column.invoke {
                        name = "foo"
                        type = "struct<bar: INT>"
                    },
                )
            }
        }
    })
    println("${LocalTime.now()} done with update")
    glueClient.close()
    println("${LocalTime.now()} closed client")
}
