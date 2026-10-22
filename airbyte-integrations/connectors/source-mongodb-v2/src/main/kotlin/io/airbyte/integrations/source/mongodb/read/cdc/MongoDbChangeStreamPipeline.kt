/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Field
import com.mongodb.client.model.Filters
import io.airbyte.cdk.StreamIdentifier
import org.bson.Document
import org.bson.conversions.Bson

/**
 * The server-side pipeline of the change stream: only data-changing events of the configured
 * collections leave the server, and a pre-image only when a record is built from it.
 */
object MongoDbChangeStreamPipeline {

    fun build(streams: Collection<StreamIdentifier>, preImages: Boolean): List<Bson> =
        listOfNotNull(
            Aggregates.match(
                Filters.and(
                    namespaces(streams),
                    Filters.`in`("operationType", DATA_OPERATIONS),
                ),
            ),
            if (preImages) KEEP_NEEDED_PRE_IMAGES else null,
        )

    /** `$or` of the namespaces; with none, a filter no event matches (`$or: []` is rejected). */
    private fun namespaces(streams: Collection<StreamIdentifier>): Bson =
        if (streams.isEmpty()) Filters.eq("ns.coll", "")
        else
            Filters.or(
                streams.map {
                    Filters.and(Filters.eq("ns.db", it.namespace), Filters.eq("ns.coll", it.name))
                },
            )

    private val DATA_OPERATIONS: List<String> = listOf("insert", "update", "replace", "delete")
    private const val PRE_IMAGE_FIELD = "fullDocumentBeforeChange"

    /**
     * Requesting pre-images makes the server fetch one for every event; this drops it from the
     * events that are emitted from `fullDocument` so it never crosses the network for an ordinary
     * update. It stays on deletes and on updates whose lookup found the document already gone,
     * which are emitted from it.
     */
    private val KEEP_NEEDED_PRE_IMAGES: Bson =
        Aggregates.addFields(
            Field(
                PRE_IMAGE_FIELD,
                Document(
                    "\$cond",
                    listOf(
                        Document(
                            "\$or",
                            listOf(
                                Document("\$eq", listOf("\$operationType", "delete")),
                                Document(
                                    "\$in",
                                    listOf(
                                        Document("\$type", "\$fullDocument"),
                                        listOf("null", "missing"),
                                    ),
                                ),
                            ),
                        ),
                        "\$$PRE_IMAGE_FIELD",
                        "\$\$REMOVE",
                    ),
                ),
            ),
        )
}
