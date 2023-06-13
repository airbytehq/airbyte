package io.airbyte.integrations.destination.bigquery.typing_deduping;

public class TypingAndDedupingFlag {

    public static final boolean isDestinationV2() {
        // TODO: set up feature flag or pass one via an environment variable from the platform
        return true;
    }
}
