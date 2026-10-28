/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.github.dockerjava.api.command.InspectContainerResponse
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import java.time.Duration
import org.testcontainers.containers.GenericContainer
import org.testcontainers.containers.wait.strategy.Wait
import org.testcontainers.utility.DockerImageName

/**
 * A single-node replica set with authentication enabled (keyfile, root user) and the users the
 * permission tests need. Clients connect directly to the one member; the source configuration
 * carries the credentials.
 */
class MongoDbAuthReplicaSet(image: String = "mongo:7.0") :
    GenericContainer<MongoDbAuthReplicaSet>(DockerImageName.parse(image)) {

    init {
        withExposedPorts(MONGO_PORT)
        withEnv("MONGO_INITDB_ROOT_USERNAME", ROOT_USER)
        withEnv("MONGO_INITDB_ROOT_PASSWORD", PASSWORD)
        withCommand(
            "bash",
            "-c",
            "openssl rand -base64 756 > /tmp/keyfile && chmod 400 /tmp/keyfile && " +
                "chown mongodb:mongodb /tmp/keyfile && exec docker-entrypoint.sh mongod " +
                "--replSet rs0 --keyFile /tmp/keyfile --bind_ip_all " +
                "--setParameter enableTestCommands=1",
        )
        waitingFor(
            Wait.forLogMessage("(?i).*waiting for connections.*", 1)
                .withStartupTimeout(Duration.ofMinutes(2)),
        )
    }

    override fun containerIsStarted(containerInfo: InspectContainerResponse) {
        // The entrypoint restarts mongod after creating the root user; retry until it answers.
        retry("rs.initiate({_id: 'rs0', members: [{_id: 0, host: 'localhost:$MONGO_PORT'}]})")
        retry(
            "let n = 0; while (db.adminCommand({replSetGetStatus: 1}).myState != 1) " +
                "{ if (++n > 150) quit(1); sleep(200); }",
        )
        retry(
            """
            const admin = db.getSiblingDB('admin');
            admin.createUser({user: '$SINGLE_DB_USER', pwd: '$PASSWORD',
                roles: [{role: 'read', db: '$TEST_DB'}]});
            admin.createUser({user: '$ANY_DB_USER', pwd: '$PASSWORD',
                roles: [{role: 'readAnyDatabase', db: 'admin'}]});
            admin.createUser({user: '$OTHER_DB_USER', pwd: '$PASSWORD',
                roles: [{role: 'read', db: '$OTHER_DB'}]});
            admin.createRole({role: 'one_collection', roles: [], privileges: [
                {resource: {db: '$TEST_DB', collection: '$READABLE_COLLECTION'},
                 actions: ['find', 'changeStream']}]});
            admin.createUser({user: '$COLLECTION_USER', pwd: '$PASSWORD',
                roles: [{role: 'one_collection', db: 'admin'}]});
            """
                .trimIndent(),
        )
    }

    private fun retry(script: String) {
        var last: String? = null
        repeat(60) {
            val result =
                execInContainer(
                    "mongosh",
                    "--quiet",
                    "-u",
                    ROOT_USER,
                    "-p",
                    PASSWORD,
                    "--authenticationDatabase",
                    "admin",
                    "--eval",
                    script,
                )
            if (result.exitCode == 0) return
            last = result.stderr + result.stdout
            Thread.sleep(1000)
        }
        error("mongosh script did not succeed: $last")
    }

    /** What the connector is configured with; credentials go in the source configuration. */
    val connectionString: String
        get() =
            "mongodb://$host:${getMappedPort(MONGO_PORT)}/?directConnection=true" +
                "&appName=${MongoDbReadTestSupport.CONNECTOR_APP_NAME}"

    /** A client for seeding, authenticated as root. */
    fun rootClient(): MongoClient =
        MongoClients.create(
            "mongodb://$ROOT_USER:$PASSWORD@$host:${getMappedPort(MONGO_PORT)}/" +
                "?directConnection=true&authSource=admin",
        )

    companion object {
        const val MONGO_PORT = 27017
        const val ROOT_USER = "root"
        const val PASSWORD = "pw"
        const val TEST_DB = "test_db"
        const val OTHER_DB = "other_db"
        /** `read` on [TEST_DB] only. */
        const val SINGLE_DB_USER = "single_db_reader"
        /** `readAnyDatabase`. */
        const val ANY_DB_USER = "any_db_reader"
        /** `read` on [OTHER_DB] only: no privileges on [TEST_DB]. */
        const val OTHER_DB_USER = "other_db_reader"
        /** `find` on [TEST_DB].[READABLE_COLLECTION] only: no `listCollections` on the database. */
        const val COLLECTION_USER = "one_collection_reader"
        const val READABLE_COLLECTION = "people"
    }
}
