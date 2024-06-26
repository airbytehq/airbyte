/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.ContextQueryFunction
import io.airbyte.cdk.db.Database
import io.airbyte.cdk.db.factory.ConnectionFactory.create
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils.DATABASE_KEY
import io.airbyte.cdk.db.jdbc.JdbcUtils.HOST_KEY
import io.airbyte.cdk.db.jdbc.JdbcUtils.HOST_LIST_KEY
import io.airbyte.cdk.db.jdbc.JdbcUtils.PASSWORD_KEY
import io.airbyte.cdk.db.jdbc.JdbcUtils.PORT_KEY
import io.airbyte.cdk.db.jdbc.JdbcUtils.PORT_LIST_KEY
import io.airbyte.cdk.db.jdbc.JdbcUtils.USERNAME_KEY
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA
import io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT
import io.airbyte.cdk.integrations.base.ssh.SshTunnel
import io.airbyte.cdk.integrations.base.ssh.SshTunnel.Companion.sshWrap
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.TestingNamespaces.generate
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.functional.CheckedFunction
import io.airbyte.commons.io.IOs.readFile
import io.airbyte.commons.jackson.MoreMappers.initMapper
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.commons.string.Strings.addRandomSuffix
import io.airbyte.integrations.destination.redshift.RedshiftConnectionHandler.close
import io.airbyte.integrations.destination.redshift.RedshiftDestination.Companion.SSL_JDBC_PARAMETERS
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations
import java.io.IOException
import java.nio.file.Path
import java.sql.Connection
import java.util.function.Function
import java.util.stream.Collectors
import org.jooq.DSLContext
import org.jooq.Record
import org.jooq.impl.DSL

abstract class SshRedshiftDestinationBaseAcceptanceTest : JdbcDestinationAcceptanceTest() {
    protected var schemaName: String? = null

    // config from which to create / delete schemas.
    protected var baseConfig: JsonNode? = null

    // config which refers to the schema that the test is being run in.
    protected var config: JsonNode?
        // override the getter name, because the base class declares a getConfig method, which
        // clashes.
        // Eventually we should just replace the super method with a native kotlin `abstract val`.
        @JvmName("getConfig_") get() = null
        set(value) = TODO()

    private var database: Database? = null

    private var connection: Connection? = null

    private val namingResolver = RedshiftSQLNameTransformer()
    private val USER_WITHOUT_CREDS = addRandomSuffix("test_user", "_", 5)

    abstract val tunnelMethod: SshTunnel.TunnelMethod

    override val imageName: String
        get() = "airbyte/destination-redshift:dev"

    @Throws(Exception::class)
    override fun getConfig(): JsonNode {
        val configAsMap = deserializeToObjectMap(config)
        val configMapBuilder = ImmutableMap.Builder<Any, Any>().putAll(configAsMap)
        return getTunnelConfig(tunnelMethod, configMapBuilder)
    }

    protected fun getTunnelConfig(
        tunnelMethod: SshTunnel.TunnelMethod,
        builderWithSchema: ImmutableMap.Builder<Any, Any>
    ): JsonNode {
        val sshBastionHost = config!!["ssh_bastion_host"]
        val sshBastionPort = config!!["ssh_bastion_port"]
        val sshBastionUser = config!!["ssh_bastion_user"]
        val sshBastionPassword = config!!["ssh_bastion_password"]
        val sshBastionKey = config!!["ssh_bastion_key"]

        val tunnelUserPassword =
            if (tunnelMethod == SshTunnel.TunnelMethod.SSH_PASSWORD_AUTH)
                sshBastionPassword.asText()
            else ""
        val sshKey =
            if (tunnelMethod == SshTunnel.TunnelMethod.SSH_KEY_AUTH) sshBastionKey.asText() else ""

        return jsonNode(
            builderWithSchema
                .put(
                    "tunnel_method",
                    jsonNode(
                        ImmutableMap.builder<Any, Any>()
                            .put("tunnel_host", sshBastionHost)
                            .put("tunnel_method", tunnelMethod.toString())
                            .put("tunnel_port", sshBastionPort.intValue())
                            .put("tunnel_user", sshBastionUser)
                            .put("tunnel_user_password", tunnelUserPassword)
                            .put("ssh_key", sshKey)
                            .build()
                    )
                )
                .build()
        )
    }

    @get:Throws(IOException::class)
    val staticConfig: JsonNode
        get() {
            val configPath = Path.of("secrets/config_staging.json")
            val configAsString = readFile(configPath)
            return deserialize(configAsString)
        }

    override fun getFailCheckConfig(): JsonNode? {
        val invalidConfig: JsonNode = Jsons.clone(config!!)
        (invalidConfig as ObjectNode).put("password", "wrong password")
        return invalidConfig
    }

    override fun implementsNamespaces(): Boolean {
        return true
    }

    @Throws(Exception::class)
    override fun retrieveNormalizedRecords(
        env: TestDestinationEnv?,
        @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
        streamName: String?,
        namespace: String?
    ): List<JsonNode> {
        val tableName = namingResolver.getIdentifier(streamName!!)
        return retrieveRecordsFromTable(tableName, namespace)
    }

    @Throws(Exception::class)
    override fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
            .stream()
            .map<JsonNode>(Function<JsonNode, JsonNode> { j: JsonNode -> j.get(COLUMN_NAME_DATA) })
            .collect(Collectors.toList<JsonNode>())
    }

    @Throws(Exception::class)
    private fun retrieveRecordsFromTable(tableName: String, schemaName: String?): List<JsonNode> {
        return sshWrap<List<JsonNode>>(
            getConfig(),
            HOST_LIST_KEY,
            PORT_LIST_KEY,
            CheckedFunction { config: JsonNode ->
                database!!.query<List<JsonNode>> { ctx: DSLContext ->
                    ctx.fetch(
                            String.format(
                                "SELECT * FROM %s.%s ORDER BY %s ASC;",
                                schemaName,
                                tableName,
                                COLUMN_NAME_EMITTED_AT
                            )
                        )
                        .stream()
                        .map<JsonNode> { record: Record -> this.getJsonFromRecord(record) }
                        .collect(Collectors.toList<JsonNode>())
                }!!
            }
        )
    }

    override fun getTestDataComparator(): TestDataComparator {
        return RedshiftTestDataComparator()
    }

    private fun createDatabaseFromConfig(config: JsonNode?): Database {
        connection =
            create(
                config!!.get(USERNAME_KEY).asText(),
                config.get(PASSWORD_KEY).asText(),
                // we have a map<string, string>
                // but we need a map<string?, string?>
                // so just copy the map
                HashMap(SSL_JDBC_PARAMETERS),
                String.format(
                    DatabaseDriver.REDSHIFT.urlFormatString,
                    config.get(HOST_KEY).asText(),
                    config.get(PORT_KEY).asInt(),
                    config.get(DATABASE_KEY).asText()
                )
            )

        return Database(DSL.using(connection))
    }

    override val maxRecordValueLimit: Int
        get() = RedshiftSqlOperations.REDSHIFT_VARCHAR_MAX_BYTE_SIZE

    @Throws(Exception::class)
    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        baseConfig = staticConfig
        val configForSchema: JsonNode = Jsons.clone<JsonNode>(baseConfig!!)
        schemaName = generate()
        TEST_SCHEMAS.add(schemaName!!)
        (configForSchema as ObjectNode).put("schema", schemaName)
        config = configForSchema
        database = createDatabaseFromConfig(config)

        // create the schema
        sshWrap(
            getConfig(),
            HOST_LIST_KEY,
            PORT_LIST_KEY,
            CheckedConsumer<JsonNode?, Exception?> { config: JsonNode? ->
                database!!.query(
                    ContextQueryFunction { ctx: DSLContext ->
                        ctx.fetch(String.format("CREATE SCHEMA %s;", schemaName))
                    }
                )
            }
        )

        // create the user
        sshWrap(
            getConfig(),
            HOST_LIST_KEY,
            PORT_LIST_KEY,
            CheckedConsumer<JsonNode?, Exception?> { config: JsonNode? ->
                database!!.query(
                    ContextQueryFunction { ctx: DSLContext ->
                        ctx.fetch(
                            String.format(
                                "CREATE USER %s WITH PASSWORD '%s' SESSION TIMEOUT 60;",
                                USER_WITHOUT_CREDS,
                                baseConfig!!["password"].asText()
                            )
                        )
                    }
                )
            }
        )
    }

    @Throws(Exception::class)
    override fun tearDown(testEnv: TestDestinationEnv) {
        // blow away the test schema at the end.
        sshWrap(
            getConfig(),
            HOST_LIST_KEY,
            PORT_LIST_KEY,
            CheckedConsumer<JsonNode?, Exception?> { config: JsonNode? ->
                database!!.query(
                    ContextQueryFunction { ctx: DSLContext ->
                        ctx.fetch(String.format("DROP SCHEMA IF EXISTS %s CASCADE;", schemaName))
                    }
                )
            }
        )

        // blow away the user at the end.
        sshWrap(
            getConfig(),
            HOST_LIST_KEY,
            PORT_LIST_KEY,
            CheckedConsumer<JsonNode?, Exception?> { config: JsonNode? ->
                database!!.query(
                    ContextQueryFunction { ctx: DSLContext ->
                        ctx.fetch(String.format("DROP USER IF EXISTS %s;", USER_WITHOUT_CREDS))
                    }
                )
            }
        )
        close(connection!!)
    }

    companion object {
        fun deserializeToObjectMap(json: JsonNode?): Map<Any, Any> {
            val objectMapper = initMapper()
            return objectMapper.convertValue<Map<Any, Any>>(
                json,
                object : TypeReference<Map<Any, Any>?>() {}
            )
        }
    }
}
