/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.integrations.source.mongodb.MongoDbAuthReplicaSet.Companion.ANY_DB_USER
import io.airbyte.integrations.source.mongodb.MongoDbAuthReplicaSet.Companion.COLLECTION_USER
import io.airbyte.integrations.source.mongodb.MongoDbAuthReplicaSet.Companion.OTHER_DB
import io.airbyte.integrations.source.mongodb.MongoDbAuthReplicaSet.Companion.OTHER_DB_USER
import io.airbyte.integrations.source.mongodb.MongoDbAuthReplicaSet.Companion.PASSWORD
import io.airbyte.integrations.source.mongodb.MongoDbAuthReplicaSet.Companion.READABLE_COLLECTION
import io.airbyte.integrations.source.mongodb.MongoDbAuthReplicaSet.Companion.SINGLE_DB_USER
import io.airbyte.integrations.source.mongodb.MongoDbAuthReplicaSet.Companion.TEST_DB
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.assertFailure
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.configuredCatalog
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.read
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.readExpectingFailure
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.records
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationSpecification
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import org.bson.Document
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

/**
 * The privilege model, against a replica set with authentication: the `read` role on the one
 * configured database is enough (the change stream is opened on that database), several databases
 * need `readAnyDatabase` (one cluster-wide stream), and a user without privileges on a configured
 * database gets the legacy "no authorized collections" message.
 */
class MongoDbSourcePermissionsTest {

    @Test
    fun testCheckSucceedsWithReadRoleOnTheConfiguredDatabase() {
        SyncsTestFixture.testCheck(config(SINGLE_DB_USER, listOf(TEST_DB)))
    }

    @Test
    fun testCheckSucceedsWithReadAnyDatabaseOnSeveralDatabases() {
        SyncsTestFixture.testCheck(config(ANY_DB_USER, listOf(TEST_DB, OTHER_DB)))
    }

    /** No privilege at all on the database: the server's own error, as the legacy connector. */
    @Test
    fun testCheckWithoutAnyPrivilegeOnTheDatabaseIsUnauthorized() {
        SyncsTestFixture.testCheck(
            config(OTHER_DB_USER, listOf(TEST_DB)),
            expectedFailure = "not authorized to read the configured databases",
        )
    }

    /**
     * Privileges on one collection but not `listCollections` on the database: `listCollections`
     * only lists what the user can read when asked without a filter, so the connector asks that way
     * and drops views in a second, privileged command it can do without.
     */
    @Test
    fun testCollectionLevelPrivilegesListOnlyThatCollection() {
        val config = config(COLLECTION_USER, listOf(TEST_DB))
        SyncsTestFixture.testCheck(config)
        Assertions.assertEquals(
            listOf(READABLE_COLLECTION),
            MongoDbReadTestSupport.discover(config).streams.map { it.name },
        )
        val sync: BufferingOutputConsumer =
            read(config, configuredCatalog(config, SyncMode.FULL_REFRESH, setOf(COLLECTION)))
        Assertions.assertEquals(
            countOf(TEST_DB),
            records(sync, COLLECTION).size,
            "every document of the one readable collection",
        )
    }

    @Test
    fun testCheckFailsWithAWrongPassword() {
        SyncsTestFixture.testCheck(
            MongoDbTestConfigs.config(
                replicaSet.connectionString,
                listOf(TEST_DB),
                username = SINGLE_DB_USER,
                password = "not-the-password",
            ),
            expectedFailure =
                "Authentication failed.  Please check the source's configured credentials.",
        )
    }

    /** One database: the stream is opened on it, which `read` on that database allows. */
    @Test
    fun testIncrementalSyncWithReadRoleOnASingleDatabase() {
        val config = config(SINGLE_DB_USER, listOf(TEST_DB))
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config, SyncMode.INCREMENTAL, setOf(COLLECTION))
        val sync1: BufferingOutputConsumer = read(config, catalog)
        Assertions.assertEquals(countOf(TEST_DB), records(sync1, COLLECTION).size)

        replicaSet.rootClient().use { root ->
            root
                .getDatabase(TEST_DB)
                .getCollection(COLLECTION)
                .insertOne(Document("_id", 1000).append("name", "carol"))
        }
        val sync2: BufferingOutputConsumer = read(config, catalog, sync1.states())
        Assertions.assertEquals(
            listOf("carol"),
            records(sync2, COLLECTION).map { it["name"].asText() },
        )
    }

    /**
     * Several databases: the stream is cluster-wide, which `read` on one database does not allow
     * (`Unauthorized`, a configuration error), while `readAnyDatabase` does.
     */
    @Test
    fun testClusterWideChangeStreamNeedsReadAnyDatabase() {
        val anyDb = config(ANY_DB_USER, listOf(TEST_DB, OTHER_DB))
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(anyDb, SyncMode.INCREMENTAL, setOf(COLLECTION))
        Assertions.assertEquals(
            setOf(TEST_DB, OTHER_DB),
            catalog.streams.map { it.stream.namespace }.toSet(),
        )
        val singleDb = config(SINGLE_DB_USER, listOf(TEST_DB, OTHER_DB))
        val failed: BufferingOutputConsumer = readExpectingFailure(singleDb, catalog)
        assertFailure(
            failed,
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            "readAnyDatabase",
        )

        val sync: BufferingOutputConsumer = read(anyDb, catalog)
        Assertions.assertEquals(
            countOf(TEST_DB) + countOf(OTHER_DB),
            records(sync, COLLECTION).size,
            "both databases' people",
        )
    }

    /** Documents in `<db>.people` right now (tests insert into it). */
    private fun countOf(db: String): Int =
        replicaSet.rootClient().use {
            it.getDatabase(db).getCollection(COLLECTION).countDocuments().toInt()
        }

    private fun config(
        user: String,
        databases: List<String>,
    ): MongoDbSourceConfigurationSpecification =
        MongoDbTestConfigs.config(
            replicaSet.connectionString,
            databases,
            username = user,
            password = PASSWORD,
        )

    companion object {
        const val COLLECTION = "people"

        lateinit var replicaSet: MongoDbAuthReplicaSet

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            replicaSet = MongoDbAuthReplicaSet().also { it.start() }
            replicaSet.rootClient().use { root ->
                root
                    .getDatabase(TEST_DB)
                    .getCollection(COLLECTION)
                    .insertMany(
                        listOf(
                            Document("_id", 1).append("name", "alice"),
                            Document("_id", 2).append("name", "bob"),
                        ),
                    )
                root
                    .getDatabase(TEST_DB)
                    .getCollection("secrets")
                    .insertOne(Document("_id", 1).append("token", "hidden"))
                root
                    .getDatabase(OTHER_DB)
                    .getCollection(COLLECTION)
                    .insertOne(Document("_id", 1).append("name", "dave"))
            }
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            replicaSet.stop()
        }
    }
}
