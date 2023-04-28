package io.airbyte.integrations.destination.vertica;

import io.airbyte.integrations.destination.StandardNameTransformer;

public class VerticaNameTransformer extends StandardNameTransformer {

    @Override
    public String getRawTableName(final String streamName) {
        final String rawTableName = applyDefaultCase(super.getRawTableName(streamName));
        return rawTableName.substring(13,rawTableName.length());
    }

}