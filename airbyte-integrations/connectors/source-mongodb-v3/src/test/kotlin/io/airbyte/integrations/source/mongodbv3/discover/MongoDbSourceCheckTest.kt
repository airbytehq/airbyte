/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.discover

import com.mongodb.client.MongoClients
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.integrations.source.mongodbv3.MongoDbTestConfigs.config
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
        // Same actionable message as source-mongodb-v2, naming the unreadable database.
        SyncsTestFixture.testCheck(
            config(replicaSet.connectionString, listOf("does_not_exist")),
            expectedFailure =
                "Target MongoDB databases do not contain any authorized collections. " +
                    "Databases without permissions: does_not_exist",
        )
    }

    @Test
    fun testCheckNamesEveryDatabaseWithoutAuthorizedCollections() {
        SyncsTestFixture.testCheck(
            config(replicaSet.connectionString, listOf("nope_one", "nope_two")),
            expectedFailure = "Databases without permissions: nope_one, nope_two",
        )
    }

    /** A standalone `mongod` has no oplog, so change streams can never work: fail at `check`. */
    @Test
    fun testCheckFailsAgainstStandaloneInstance() {
        SyncsTestFixture.testCheck(
            config(standaloneConnectionString(), listOf(DATABASE)),
            expectedFailure = "standalone server, which has no oplog",
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
            expectedFailure =
                "Authentication failed.  Please check the source's configured credentials.",
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
            for (connectionString in
                listOf(replicaSet.connectionString, standaloneConnectionString())) {
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
    }
}
