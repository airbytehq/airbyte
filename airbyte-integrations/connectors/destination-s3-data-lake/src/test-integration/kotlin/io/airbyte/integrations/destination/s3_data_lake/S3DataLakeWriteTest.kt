/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.icerberg.parquet.IcebergWriteTest
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.integrations.destination.s3_data_lake.catalog.GlueTableIdGenerator
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeSpecification
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.nio.file.Files
import java.util.Base64
import kotlin.test.assertContains
import okhttp3.FormBody
import okhttp3.OkHttpClient
import okhttp3.Request
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

abstract class S3DataLakeWriteTest(
    configContents: String,
    tableIdGenerator: TableIdGenerator,
    getCatalog:
        (io.airbyte.cdk.command.ConfigurationSpecification) -> org.apache.iceberg.catalog.Catalog,
    cleaner: DestinationCleaner = io.airbyte.cdk.load.test.util.NoopDestinationCleaner,
    micronautProperties: Map<Property, String> = emptyMap(),
    enableSpeed: Boolean = false,
) :
    IcebergWriteTest(
        configContents,
        S3DataLakeSpecification::class.java,
        getCatalog,
        cleaner,
        tableIdGenerator,
        additionalMicronautEnvs = S3DataLakeDestination.additionalMicronautEnvs,
        micronautProperties = micronautProperties,
        enableSpeed = enableSpeed,
    ) {
    /** Returns [config] with the `lowercase_column_names` option enabled. */
    protected fun withLowercaseColumnNames(config: String): String {
        val mapper = ObjectMapper()
        val node = mapper.readTree(config) as ObjectNode
        node.put("lowercase_column_names", true)
        return mapper.writeValueAsString(node)
    }
}

class GlueWriteTest :
    S3DataLakeWriteTest(
        configContents = Files.readString(S3DataLakeTestUtil.GLUE_CONFIG_PATH),
        tableIdGenerator = GlueTableIdGenerator(null),
        getCatalog = { spec ->
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.getConfig(spec),
                S3DataLakeTestUtil.getAwsAssumeRoleCredentials(),
            )
        },
        cleaner = S3DataLakeCleaner,
        micronautProperties =
            S3DataLakeTestUtil.getAwsAssumeRoleCredentials().asMicronautProperties(),
    ) {
    @Test
    fun testNameConflicts() {
        assumeTrue(verifyDataWriting)

        fun makeStream(
            name: String,
            namespaceSuffix: String,
        ) =
            DestinationStream(
                unmappedNamespace = randomizedNamespace + namespaceSuffix,
                unmappedName = name,
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper(),
                tableSchema = makeTableSchema(ObjectType(linkedMapOf("id" to intType)), Append),
            )
        // Glue downcases stream IDs, and also coerces to alphanumeric+underscore.
        // So these two streams will collide.
        val catalog =
            DestinationCatalog(
                listOf(
                    makeStream("stream_with_spécial_character", "_foo"),
                    makeStream("STREAM_WITH_SPÉCIAL_CHARACTER", "_FOO"),
                ),
            )

        val failure = expectFailure { runSync(updatedConfig, catalog, messages = emptyList()) }
        assertContains(failure.message, "Detected naming conflicts between streams")
    }

    @Test
    override fun testBasicTypes() {
        super.testBasicTypes()
    }

    /**
     * Iceberg supports recursing into arrays, which is unusual from other connectors. Add a test
     * that we correctly recurse through these values.
     */
    @Test
    fun testNestedArrayCoercion() {
        val nestedArraySchema =
            ObjectType(
                linkedMapOf(
                    "id" to intType,
                    "array" to
                        FieldType(
                            ArrayType(FieldType(NumberType, nullable = true)),
                            nullable = true,
                        ),
                ),
            )
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper(),
                tableSchema = makeTableSchema(nestedArraySchema, Append),
            )

        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """
                    {
                      "id": 1,
                      "array": [42, "potato"]
                    }
                    """.trimIndent(),
                    emittedAtMs = 100,
                ),
            ),
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 100,
                    generationId = 42,
                    // 42 -> 42.0; potato -> null
                    data = mapOf("id" to 1, "array" to listOf(42.0, null)),
                    airbyteMeta =
                        OutputRecord.Meta(
                            syncId = 42,
                            changes =
                                listOf(
                                    Meta.Change(
                                        "array.1",
                                        Change.NULLED,
                                        Reason.DESTINATION_SERIALIZATION_ERROR,
                                    ),
                                ),
                        ),
                ),
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    @Test
    fun testLowercaseColumnNames() {
        assumeTrue(verifyDataWriting)
        val schema =
            ObjectType(
                linkedMapOf(
                    "Id" to intType,
                    "URLs" to stringType,
                    "createdAt" to stringType,
                    "Foo.Bar" to stringType,
                    "already_lowercase" to stringType,
                ),
            )
        fun makeStream(syncId: Long) =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_lowercase_columns",
                generationId = 0,
                minimumGenerationId = 0,
                syncId = syncId,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = makeTableSchema(schema, Append),
            )
        val config = withLowercaseColumnNames(updatedConfig)

        val firstStream = makeStream(syncId = 42)
        runSync(
            config,
            firstStream,
            listOf(
                InputRecord(
                    firstStream,
                    """{"Id": 1, "URLs": "https://a", "createdAt": "2000-01-01", "Foo.Bar": "foo", "already_lowercase": "bar"}""",
                    emittedAtMs = 1000,
                    checkpointId = checkpointKeyForMedium()?.checkpointId,
                ),
            ),
        )
        // A second sync against the same table must not see the lowercased columns as a schema
        // change (i.e. no drop + re-add).
        val secondStream = makeStream(syncId = 43)
        runSync(
            config,
            secondStream,
            listOf(
                InputRecord(
                    secondStream,
                    """{"Id": 2, "URLs": "https://b", "createdAt": "2001-01-01", "Foo.Bar": "baz", "already_lowercase": "qux"}""",
                    emittedAtMs = 2000,
                    checkpointId = checkpointKeyForMedium()?.checkpointId,
                ),
            ),
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1000,
                    generationId = 0,
                    data =
                        mapOf(
                            "id" to 1,
                            "urls" to "https://a",
                            "createdat" to "2000-01-01",
                            "foo.bar" to "foo",
                            "already_lowercase" to "bar",
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 2000,
                    generationId = 0,
                    data =
                        mapOf(
                            "id" to 2,
                            "urls" to "https://b",
                            "createdat" to "2001-01-01",
                            "foo.bar" to "baz",
                            "already_lowercase" to "qux",
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                ),
            ),
            secondStream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    @Test
    fun testLowercaseColumnNamesDedup() {
        assumeTrue(verifyDataWriting)
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_lowercase_columns_dedup",
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema =
                    makeTableSchema(
                        ObjectType(
                            linkedMapOf(
                                "RecordId" to intType,
                                "updatedAt" to intType,
                                "userName" to stringType,
                            ),
                        ),
                        Dedupe(
                            primaryKey = listOf(listOf("RecordId")),
                            cursor = listOf("updatedAt")
                        ),
                    ),
            )

        runSync(
            withLowercaseColumnNames(updatedConfig),
            stream,
            listOf(
                InputRecord(
                    stream,
                    """{"RecordId": 1, "updatedAt": 1, "userName": "Alice1"}""",
                    emittedAtMs = 1000,
                    checkpointId = checkpointKeyForMedium()?.checkpointId,
                ),
                InputRecord(
                    stream,
                    """{"RecordId": 1, "updatedAt": 2, "userName": "Alice2"}""",
                    emittedAtMs = 2000,
                    checkpointId = checkpointKeyForMedium()?.checkpointId,
                ),
            ),
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 2000,
                    generationId = 42,
                    data = mapOf("recordid" to 1, "updatedat" to 2, "username" to "Alice2"),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
            ),
            stream,
            primaryKey = listOf(listOf("recordid")),
            cursor = listOf("updatedat"),
        )
    }

    @Test
    fun testLowercaseColumnNamesRequiresRefreshOnExistingTable() {
        assumeTrue(verifyDataWriting)
        val schema = ObjectType(linkedMapOf("Id" to intType, "userName" to stringType))
        fun makeStream(syncId: Long, generationId: Long, minimumGenerationId: Long) =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_lowercase_columns_existing_table",
                generationId = generationId,
                minimumGenerationId = minimumGenerationId,
                syncId = syncId,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = makeTableSchema(schema, Append),
            )
        fun record(stream: DestinationStream, id: Int, name: String, emittedAtMs: Long) =
            InputRecord(
                stream,
                """{"Id": $id, "userName": "$name"}""",
                emittedAtMs = emittedAtMs,
                checkpointId = checkpointKeyForMedium()?.checkpointId,
            )

        // 1. Create the table with the option disabled: columns keep their original case.
        val initialStream = makeStream(syncId = 42, generationId = 0, minimumGenerationId = 0)
        runSync(updatedConfig, initialStream, listOf(record(initialStream, 1, "Alice", 1000)))

        // 2. Enabling the option on an incremental sync must fail instead of dropping the
        //    mixed-case columns.
        val incrementalStream = makeStream(syncId = 43, generationId = 0, minimumGenerationId = 0)
        val failure = expectFailure {
            runSync(
                withLowercaseColumnNames(updatedConfig),
                incrementalStream,
                listOf(record(incrementalStream, 2, "Bob", 2000)),
            )
        }
        assertContains(failure.message, "userName -> username")

        // 3. A truncate refresh recreates the table with lowercase column names.
        val refreshStream = makeStream(syncId = 44, generationId = 1, minimumGenerationId = 1)
        runSync(
            withLowercaseColumnNames(updatedConfig),
            refreshStream,
            listOf(record(refreshStream, 3, "Carol", 3000)),
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 3000,
                    generationId = 1,
                    data = mapOf("id" to 3, "username" to "Carol"),
                    airbyteMeta = OutputRecord.Meta(syncId = 44),
                ),
            ),
            refreshStream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }
}

class GlueAssumeRoleWriteTest :
    S3DataLakeWriteTest(
        configContents = Files.readString(S3DataLakeTestUtil.GLUE_ASSUME_ROLE_CONFIG_PATH),
        tableIdGenerator = GlueTableIdGenerator(null),
        getCatalog = { spec ->
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.getConfig(spec),
                S3DataLakeTestUtil.getAwsAssumeRoleCredentials(),
            )
        },
        cleaner = S3DataLakeCleaner,
        micronautProperties =
            S3DataLakeTestUtil.getAwsAssumeRoleCredentials().asMicronautProperties(),
    )

@Disabled("Tests failing in master")
class NessieMinioWriteTest :
    S3DataLakeWriteTest(
        configContents = getConfig(),
        tableIdGenerator = SimpleTableIdGenerator(),
        getCatalog = { spec ->
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.getConfig(spec as S3DataLakeSpecification),
                S3DataLakeTestUtil.getAwsAssumeRoleCredentials(),
            )
        },
    ) {
    companion object {
        private fun getToken(): String {
            val client = OkHttpClient()
            val objectMapper = ObjectMapper()

            val credentials = "client1:s3cr3t"
            val encodedCredentials = Base64.getEncoder().encodeToString(credentials.toByteArray())

            val formBody =
                FormBody.Builder()
                    .add("grant_type", "client_credentials")
                    .add("scope", "profile")
                    .build()

            val request =
                Request.Builder()
                    .url("http://127.0.0.1:8080/realms/iceberg/protocol/openid-connect/token")
                    .post(formBody)
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .header("Authorization", "Basic $encodedCredentials")
                    .build()

            val response = client.newCall(request).execute()
            val jsonResponse = response.body?.string() ?: throw RuntimeException("Empty response")
            val jsonNode: JsonNode = objectMapper.readTree(jsonResponse)
            return jsonNode.get("access_token").asText()
        }

        fun getConfig(): String {
            val minioEndpoint = NessieTestContainers.testcontainers.getServiceHost("minio", 9000)
            val nessieEndpoint = NessieTestContainers.testcontainers.getServiceHost("nessie", 19120)

            val authToken = getToken()
            return """
                {
                    "catalog_type": {
                      "catalog_type": "NESSIE",
                      "server_uri": "http://$nessieEndpoint:19120/api/v1",
                      "access_token": "$authToken",
                      "namespace": "<DEFAULT_NAMESPACE_PLACEHOLDER>"
                    },
                    "s3_bucket_name": "demobucket",
                    "s3_bucket_region": "us-east-1",
                    "access_key_id": "minioadmin",
                    "secret_access_key": "minioadmin",
                    "s3_endpoint": "http://$minioEndpoint:9002",
                    "warehouse_location": "s3://demobucket/",
                    "main_branch_name": "main"
                }
                """.trimIndent()
        }

        @JvmStatic
        @BeforeAll
        fun setup() {
            NessieTestContainers.start()
        }
    }
}

// the basic REST catalog behaves poorly with multithreading,
// even across multiple streams.
// so run singlethreaded.
@Execution(ExecutionMode.SAME_THREAD)
@Disabled("Tests failing in master")
class RestWriteTest :
    S3DataLakeWriteTest(
        getConfig(),
        SimpleTableIdGenerator(),
        { spec ->
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.getConfig(spec as S3DataLakeSpecification),
                null,
            )
        },
    ) {
    @Test
    @Disabled("https://github.com/airbytehq/airbyte-internal-issues/issues/11439")
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

    override val manyStreamCount = 5

    @Disabled("This doesn't seem to work with concurrency, etc.")
    @Test
    override fun testManyStreamsCompletion() {
        super.testManyStreamsCompletion()
    }

    companion object {
        fun getConfig(): String {
            // We retrieve the ephemeral host/port from the updated RestTestContainers
            val minioEndpoint = RestTestContainers.testcontainers.getServiceHost("minio", 9000)
            val restEndpoint = RestTestContainers.testcontainers.getServiceHost("rest", 8181)

            return """
                {
                    "catalog_type": {
                      "catalog_type": "REST",
                      "server_uri": "http://$restEndpoint:8181",
                      "namespace": "<DEFAULT_NAMESPACE_PLACEHOLDER>"
                    },
                    "s3_bucket_name": "warehouse",
                    "s3_bucket_region": "us-east-1",
                    "access_key_id": "admin",
                    "secret_access_key": "password",
                    "s3_endpoint": "http://$minioEndpoint:9100",
                    "warehouse_location": "s3://warehouse/",
                    "main_branch_name": "main"
                }
                """.trimIndent()
        }

        @JvmStatic
        @BeforeAll
        fun setup() {
            // Start the testcontainers environment once before any tests run
            RestTestContainers.start()
        }
    }
}

@Execution(ExecutionMode.SAME_THREAD)
@Disabled("Tests failing in master")
class PolarisWriteTest :
    S3DataLakeWriteTest(
        configContents = getConfig(),
        tableIdGenerator = SimpleTableIdGenerator(),
        getCatalog = { spec ->
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.getConfig(spec as S3DataLakeSpecification),
                null,
            )
        },
    ) {
    @Test
    @Disabled("https://github.com/airbytehq/airbyte-internal-issues/issues/11439")
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

    companion object {
        fun getConfig(): String = PolarisEnvironment.getConfig()

        @JvmStatic
        @BeforeAll
        fun setup() {
            PolarisEnvironment.startServices()
        }

        @JvmStatic
        @AfterAll
        fun stop() {
            PolarisEnvironment.stopServices()
        }
    }
}

class GlueWriteTestProtoSocket :
    S3DataLakeWriteTest(
        configContents = Files.readString(S3DataLakeTestUtil.GLUE_CONFIG_PATH),
        tableIdGenerator = GlueTableIdGenerator(null),
        getCatalog = { spec ->
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.getConfig(spec),
                S3DataLakeTestUtil.getAwsAssumeRoleCredentials(),
            )
        },
        cleaner = S3DataLakeCleaner,
        micronautProperties =
            S3DataLakeTestUtil.getAwsAssumeRoleCredentials().asMicronautProperties(),
        enableSpeed = true,
    ) {
    // Use single socket for dedup tests to preserve record ordering in proto socket mode
    override val useSingleSocketForDedup: Boolean = true

    @Disabled("https://github.com/airbytehq/airbyte-internal-issues/issues/15495")
    @Test
    override fun testContainerTypes() {
        super.testContainerTypes()
    }
}
