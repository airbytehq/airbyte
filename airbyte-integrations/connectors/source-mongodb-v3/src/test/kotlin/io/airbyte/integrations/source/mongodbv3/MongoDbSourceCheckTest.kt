/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.MongoClients
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.util.Jsons
import org.bson.Document
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.GenericContainer
import org.testcontainers.containers.MongoDBContainer
import org.testcontainers.utility.DockerImageName

/** Runs the CHECK operation against real `mongod` containers. */
class MongoDbSourceCheckTest {

    @Test
    fun testCheckSucceedsAgainstReplicaSet() {
        SyncsTestFixture.testCheck(config(replicaSet.connectionString, listOf(DATABASE)))
    }

    @Test
    fun testCheckSucceedsWithMultipleDatabasesWhenOneIsReadable() {
        SyncsTestFixture.testCheck(
            config(replicaSet.connectionString, listOf("does_not_exist", DATABASE)),
        )
    }

    @Test
    fun testCheckFailsWithoutAuthorizedCollections() {
        SyncsTestFixture.testCheck(
            config(replicaSet.connectionString, listOf("does_not_exist")),
            expectedFailure = "Discovered zero tables",
        )
    }

    @Test
    fun testCheckFailsAgainstStandaloneInstance() {
        SyncsTestFixture.testCheck(
            config(standaloneConnectionString(), listOf(DATABASE)),
            expectedFailure = "Target MongoDB instance is not a replica set cluster",
        )
    }

    @Test
    fun testCheckFailsWhenUnreachable() {
        SyncsTestFixture.testCheck(
            config("mongodb://localhost:1/?serverSelectionTimeoutMS=2000", listOf(DATABASE)),
            expectedFailure = "Timed out while waiting for a server that matches",
        )
    }

    @Test
    fun testCheckFailsWithoutDatabases() {
        SyncsTestFixture.testCheck(
            config(replicaSet.connectionString, emptyList()),
            expectedFailure = "No databases specified in the configuration.",
        )
    }

    @Test
    fun testCheckFailsWithBadCredentials() {
        SyncsTestFixture.testCheck(
            config(replicaSet.connectionString, listOf(DATABASE), username = "u", password = "p"),
            expectedFailure = "Authentication failed.  Please check the source's configured credentials.",
        )
    }

    companion object {
        const val DATABASE = "test_db"
        const val COLLECTION = "people"
        val IMAGE: DockerImageName = DockerImageName.parse("mongo:7.0")

        lateinit var replicaSet: MongoDBContainer
        lateinit var standalone: GenericContainer<*>

        @JvmStatic
        @BeforeAll
        fun startContainers() {
            replicaSet = MongoDBContainer(IMAGE).also { it.start() }
            standalone = GenericContainer(IMAGE).withExposedPorts(27017).also { it.start() }
            for (connectionString in listOf(replicaSet.connectionString, standaloneConnectionString())) {
                MongoClients.create(connectionString).use { client ->
                    client
                        .getDatabase(DATABASE)
                        .getCollection(COLLECTION)
                        .insertMany(
                            listOf(
                                Document("name", "alice").append("age", 30),
                                Document("name", "bob").append("age", 41),
                            ),
                        )
                }
            }
        }

        @JvmStatic
        @AfterAll
        fun stopContainers() {
            replicaSet.stop()
            standalone.stop()
        }

        fun standaloneConnectionString(): String =
            "mongodb://${standalone.host}:${standalone.getMappedPort(27017)}/"

        fun config(
            connectionString: String,
            databases: List<String>,
            username: String? = null,
            password: String? = null,
        ): MongoDbSourceConfigurationSpecification {
            val databaseConfig: MutableMap<String, Any> =
                mutableMapOf(
                    "cluster_type" to "SELF_MANAGED_REPLICA_SET",
                    "connection_string" to connectionString,
                    "databases" to databases,
                )
            username?.let { databaseConfig["username"] = it }
            password?.let { databaseConfig["password"] = it }
            val json: String =
                Jsons.writeValueAsString(mapOf("database_config" to databaseConfig))
            return Jsons.readValue(json, MongoDbSourceConfigurationSpecification::class.java)
        }
    }
}
