/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.mongodb.MongoClientSettings
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Projections
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.integrations.source.mongodb.config.MongoDbClientFactory
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfiguration
import io.airbyte.integrations.source.mongodb.read.cdc.MongoDbResumeTokens
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbIdTypes
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.Instant
import org.bson.BsonDocument
import org.bson.BsonTimestamp
import org.bson.Document

private val log = KotlinLogging.logger {}

/**
 * Lines logged from cheap server calls so a sync's logs say what it talked to, how far back the
 * oplog goes relative to the saved position, and how big each collection is. A call that fails is
 * one warning with the server's message, never an error: nothing here changes what the sync does.
 */
object MongoDbDiagnostics {

    /** Logs what [client] is connected to; call once per client. */
    fun logConnection(client: MongoClient, configuration: MongoDbSourceConfiguration) {
        logGuarded("the server's connection details") {
            connectionLine(client, MongoDbClientFactory.settings(configuration))
        }
    }

    /**
     * Logs [line], or one warning naming [what] when it cannot be built. The line is built outside
     * the logger's lambda, whose failures the logging library swallows into an INFO.
     */
    fun logGuarded(what: String, line: () -> String) {
        val text: String =
            try {
                line()
            } catch (e: Exception) {
                log.warn { "Could not read $what (${e.message}); continuing." }
                return
            }
        log.info { text }
    }

    fun connectionLine(client: MongoClient, settings: MongoClientSettings): String {
        val admin = client.getDatabase(ADMIN)
        val hello: Document = admin.runCommand(Document(HELLO, 1))
        val version: String = admin.runCommand(Document("buildInfo", 1)).getString("version")
        val topology: String =
            when {
                hello.getString("msg") == MONGOS -> "sharded cluster via mongos"
                hello.containsKey("setName") -> "replica set \"${hello.getString("setName")}\""
                else -> "standalone server"
            }
        val role: String? =
            when {
                hello.getBoolean("isWritablePrimary", false) -> "primary"
                hello.getBoolean("secondary", false) -> "secondary"
                else -> null
            }
        val member: String =
            hello.getString("me")?.let {
                ", answering member $it${role?.let { r -> " ($r)" } ?: ""}"
            } ?: ""
        val hosts: String = hello.getList("hosts", String::class.java)?.let { ", hosts $it" } ?: ""
        val compression: String =
            settings.compressorList.joinToString(",") { it.name }.ifEmpty { "none" }
        return "Connected to MongoDB $version, $topology$member$hosts, wire version " +
            "${hello["maxWireVersion"]}; TLS ${if (settings.sslSettings.isEnabled) "on" else "off"}, " +
            "read preference ${settings.readPreference.name}, compression requested $compression."
    }

    /**
     * The oplog's size, entry count and time window, and where [savedToken] (the saved change
     * stream position, decoded to its oplog time here so a malformed one is this line's failure,
     * not the sync's) stands in it. The `local` database holds the oplog of one member, so there is
     * nothing to read through a `mongos`.
     */
    fun oplogLine(client: MongoClient, savedToken: BsonDocument?): String {
        val hello: Document = client.getDatabase(ADMIN).runCommand(Document(HELLO, 1))
        if (hello.getString("msg") == MONGOS) {
            return "Oplog statistics are per shard and not available through mongos."
        }
        val local = client.getDatabase("local")
        val stats: Document = local.runCommand(Document(COLL_STATS, OPLOG))
        val oplog: MongoCollection<Document> = local.getCollection(OPLOG)
        val oldest: BsonTimestamp = endpointTime(oplog, 1)
        val newest: BsonTimestamp = endpointTime(oplog, -1)
        val position: String =
            savedToken?.let(MongoDbResumeTokens::timestamp)?.let {
                " Saved position ${instant(it)} is " +
                    if (it < oldest) {
                        "OLDER than the oldest entry: the change stream cannot resume from it."
                    } else {
                        "${hours(oldest, it)} h inside the window."
                    }
            } ?: ""
        return "Oplog: ${bytes(stats.long("size"))} used of ${bytes(stats.long("maxSize"))}, " +
            "${count(stats.long("count"))} entries, ${instant(oldest)} to ${instant(newest)} " +
            "(window ${hours(oldest, newest)} h).$position"
    }

    /**
     * The collection's document count, sizes and index count (totals over the shards through a
     * `mongos`), and the kind of its smallest `_id`: the `_id` index orders by BSON type before
     * value and a resume filter `_id > x` only matches x's kind, so that is the kind a resumed
     * snapshot follows. The `collStats` command rather than the `$collStats` stage, so that no
     * diagnostic is an `aggregate`.
     */
    fun collectionLine(client: MongoClient, streamId: StreamIdentifier): String {
        val database = client.getDatabase(streamId.namespace!!)
        val stats: Document = database.runCommand(Document(COLL_STATS, streamId.name))
        val count: Long = stats.long("count")
        val size: Long = stats.long("size")
        val storageSize: Long = stats.long("storageSize")
        val indexes: Long = stats.long("nindexes")
        val idTypes: List<String> = MongoDbIdTypes.present(database.getCollection(streamId.name))
        val average: String = if (count > 0) " (avg ${bytes(size / count)})" else ""
        val types: String = if (idTypes.isEmpty()) "" else "; _id types $idTypes"
        return "Snapshot of ${streamId.namespace}.${streamId.name}: ${count(count)} documents, " +
            "${bytes(size)}$average, ${bytes(storageSize)} on disk, $indexes indexes$types."
    }

    private fun endpointTime(oplog: MongoCollection<Document>, order: Int): BsonTimestamp =
        oplog
            .find()
            .projection(Projections.include(TS_FIELD))
            .sort(Document(NATURAL_ORDER, order))
            .limit(1)
            .first()
            ?.get(TS_FIELD, BsonTimestamp::class.java) ?: error("the oplog is empty")

    /** `collStats` sizes are `Int` while they fit and `Long` past that. */
    private fun Document.long(field: String): Long = (get(field) as? Number)?.toLong() ?: 0L

    private fun instant(timestamp: BsonTimestamp): Instant =
        Instant.ofEpochSecond(timestamp.time.toLong())

    private fun hours(from: BsonTimestamp, to: BsonTimestamp): String =
        "%.1f".format(Duration.between(instant(from), instant(to)).toMinutes() / 60.0)

    private fun count(n: Long): String = "%,d".format(n)

    private fun bytes(n: Long): String =
        when {
            n >= 1L shl 30 -> "%.1f GB".format(n / (1L shl 30).toDouble())
            n >= 1L shl 20 -> "%.1f MB".format(n / (1L shl 20).toDouble())
            n >= 1L shl 10 -> "%.1f KB".format(n / (1L shl 10).toDouble())
            else -> "$n B"
        }

    private const val ADMIN = "admin"
    private const val COLL_STATS = "collStats"
    private const val OPLOG = "oplog.rs"
    private const val HELLO = "hello"
    private const val MONGOS = "isdbgrid"
    private const val TS_FIELD = "ts"
    private const val NATURAL_ORDER = "\$natural"
}
