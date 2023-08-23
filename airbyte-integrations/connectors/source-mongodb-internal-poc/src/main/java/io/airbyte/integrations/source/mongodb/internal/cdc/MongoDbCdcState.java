package io.airbyte.integrations.source.mongodb.internal.cdc;

/**
 * Represents the global CDC state that is used by Debezium as an offset.
 *
 * @param seconds The seconds component of a timestamp.
 * @param order The order component of a timestmap.
 * @param resumeToken The resume token of the most recently processed change event.
 */
public record MongoDbCdcState(int seconds, int order, String resumeToken) {
}
