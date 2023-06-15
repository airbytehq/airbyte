package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.integrations.base.DestinationConfig;

public class TypingAndDedupingFlag {

    public static final boolean isDestinationV2() {
        return DestinationConfig.getInstance().getBooleanValue("use_1s1t_format");
    }
}
