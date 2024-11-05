package io.airbyte.integrations.destination.edgao_iceberg_experiment

import aws.sdk.kotlin.runtime.auth.credentials.StaticCredentialsProvider
import aws.sdk.kotlin.services.glue.GlueClient
import aws.sdk.kotlin.services.glue.model.CreateTableRequest
import io.airbyte.cdk.util.Jsons
import java.io.File
import kotlinx.coroutines.runBlocking

fun main(): Unit = runBlocking {
    val s3Config = Jsons.readTree(File("/Users/edgao/code/airbyte/airbyte-integrations/connectors/destination-edgao-iceberg-experiment/secrets/s3.json"))
    val accessKeyId = s3Config["access_key_id"].asText()
    val secretAccessKey = s3Config["secret_access_key"].asText()
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
    }
    glueClient.createTable(CreateTableRequest.invoke {
        catalogId = "edgao_test_catalog"
        databaseName = "edgao_test_database"
        tableInput {
            name = "edgao_test_table"
        }
    })
}
