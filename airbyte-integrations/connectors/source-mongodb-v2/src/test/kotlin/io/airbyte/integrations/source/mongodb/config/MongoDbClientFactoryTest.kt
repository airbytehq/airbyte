/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.config

import com.mongodb.MongoClientSettings
import com.mongodb.ReadPreference
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.MongoDbTestConfigs
import org.bson.UuidRepresentation
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** The client settings built from a configuration: TLS, read preference, credentials, UUIDs. */
class MongoDbClientFactoryTest {

    @Test
    fun testAtlasConnectionsAlwaysUseTls() {
        val settings: MongoClientSettings =
            MongoDbClientFactory.settings(
                atlas("mongodb+srv://cluster0.abcd1.mongodb.net/", username = "u", password = "p"),
            )
        Assertions.assertTrue(settings.sslSettings.isEnabled)
    }

    @Test
    fun testSelfManagedTlsFollowsTheConnectionString() {
        Assertions.assertFalse(
            MongoDbClientFactory.settings(selfManaged("mongodb://host1:27017/"))
                .sslSettings
                .isEnabled,
        )
        Assertions.assertTrue(
            MongoDbClientFactory.settings(selfManaged("mongodb://host1:27017/?tls=true"))
                .sslSettings
                .isEnabled,
        )
    }

    @Test
    fun testReadPreferenceDefaultsToSecondaryPreferredUnlessTheStringSetsOne() {
        Assertions.assertEquals(
            ReadPreference.secondaryPreferred(),
            MongoDbClientFactory.settings(selfManaged("mongodb://host1:27017/")).readPreference,
        )
        Assertions.assertEquals(
            ReadPreference.primary(),
            MongoDbClientFactory.settings(
                    selfManaged("mongodb://host1:27017/?readPreference=primary"),
                )
                .readPreference,
        )
    }

    /** Binaries are emitted as their bytes, so the connection string must not change decoding. */
    @Test
    fun testCompressionDefaultsToSnappyThenZlibUnlessTheStringSetsCompressors() {
        fun compressors(connectionString: String): List<String> =
            MongoDbClientFactory.settings(selfManaged(connectionString)).compressorList.map {
                it.name
            }
        Assertions.assertEquals(listOf("snappy", "zlib"), compressors("mongodb://host1:27017/"))
        Assertions.assertEquals(
            listOf("zlib"),
            compressors("mongodb://host1:27017/?compressors=zlib&zlibCompressionLevel=3"),
        )
        Assertions.assertEquals(
            emptyList<String>(),
            compressors("mongodb://host1:27017/?readPreference=primary&compressors="),
            "an empty option turns compression off",
        )
    }

    @Test
    fun testUuidRepresentationIsPinnedWhateverTheConnectionStringSays() {
        Assertions.assertEquals(
            UuidRepresentation.UNSPECIFIED,
            MongoDbClientFactory.settings(
                    selfManaged("mongodb://host1:27017/?uuidRepresentation=standard"),
                )
                .uuidRepresentation,
        )
    }

    @Test
    fun testCredentialsUseTheAuthSourceAndUrlEncodeTheUsername() {
        val settings: MongoClientSettings =
            MongoDbClientFactory.settings(
                selfManaged("mongodb://host1:27017/", username = "us@er:x", password = "p@ss"),
            )
        val credential = checkNotNull(settings.credential)
        Assertions.assertEquals("us%40er%3Ax", credential.userName)
        Assertions.assertEquals("admin", credential.source)
        Assertions.assertEquals("p@ss", String(checkNotNull(credential.password)))
    }

    @Test
    fun testNoCredentialsWithoutAUsernameAndPassword() {
        Assertions.assertNull(
            MongoDbClientFactory.settings(selfManaged("mongodb://host1:27017/")).credential,
        )
    }

    @Test
    fun testConnectionStringOptionsAreHonoured() {
        val settings: MongoClientSettings =
            MongoDbClientFactory.settings(
                selfManaged("mongodb://host1:27017/?appName=airbyte-test&replicaSet=rs0"),
            )
        Assertions.assertEquals("airbyte-test", settings.applicationName)
        Assertions.assertEquals("rs0", settings.clusterSettings.requiredReplicaSetName)
    }

    private fun selfManaged(
        connectionString: String,
        username: String? = null,
        password: String? = null,
    ): MongoDbSourceConfiguration =
        MongoDbSourceConfigurationFactory()
            .makeWithoutExceptionHandling(
                MongoDbTestConfigs.config(
                    connectionString,
                    listOf("db"),
                    username = username,
                    password = password,
                ),
            )

    private fun atlas(
        connectionString: String,
        username: String,
        password: String,
    ): MongoDbSourceConfiguration =
        MongoDbSourceConfigurationFactory()
            .makeWithoutExceptionHandling(
                Jsons.readValue(
                    """
                    {"database_config": {"cluster_type": "ATLAS_REPLICA_SET",
                      "connection_string": "$connectionString", "databases": ["db"],
                      "username": "$username", "password": "$password", "auth_source": "admin"}}
                    """
                        .trimIndent(),
                    MongoDbSourceConfigurationSpecification::class.java,
                ),
            )
}
