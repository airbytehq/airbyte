package io.airbyte.integrations.destination_async;

import io.airbyte.protocol.models.v0.DestinationSyncMode;
import org.joda.time.DateTime;

/**
 * This is a duplicate of the WriteConfig class in the bases-destination-jdbc package. This is duplicated as
 * it is easier than a migration. In the long term, all usages should move over to this class.
 */
public record WriteConfig(String streamName, String namespace, String outputSchemaName, String tmpTableName,
                          String outputTableName, DestinationSyncMode syncMode, DateTime writeDateTime) {
    @Override
    public String toString() {
        return "WriteConfig{" +
                "streamName=" + streamName +
                ", namespace=" + namespace +
                ", outputSchemaName=" + outputSchemaName +
                ", tmpTableName=" + tmpTableName +
                ", outputTableName=" + outputTableName +
                ", syncMode=" + syncMode +
                '}';
    }
}
