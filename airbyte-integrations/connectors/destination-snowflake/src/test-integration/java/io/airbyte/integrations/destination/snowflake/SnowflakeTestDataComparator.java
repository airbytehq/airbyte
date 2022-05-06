package io.airbyte.integrations.destination.snowflake;

import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;

import java.util.ArrayList;
import java.util.List;

public class SnowflakeTestDataComparator extends AdvancedTestDataComparator {

    @Override
    protected List<String> resolveIdentifier(final String identifier) {
        final List<String> result = new ArrayList<>();
        final String resolved = NAME_TRANSFORMER.getIdentifier(identifier);
        result.add(identifier);
        result.add(resolved);
        if (!resolved.startsWith("\"")) {
            result.add(resolved.toLowerCase());
            result.add(resolved.toUpperCase());
        }
        return result;
    }
}
