package io.airbyte.integrations.destination.tidb;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class TiDBSQLNameTransformer extends ExtendedNameTransformer {

    @Override
    public String applyDefaultCase(final String input) {
        return input.toLowerCase();
    }

}
