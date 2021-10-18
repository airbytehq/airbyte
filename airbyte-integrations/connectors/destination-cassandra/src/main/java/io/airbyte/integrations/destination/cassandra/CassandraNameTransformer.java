package io.airbyte.integrations.destination.cassandra;

import com.google.common.base.CharMatcher;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.destination.StandardNameTransformer;

public class CassandraNameTransformer extends StandardNameTransformer {

    private final CassandraConfig cassandraConfig;

    public CassandraNameTransformer(CassandraConfig cassandraConfig) {
        this.cassandraConfig = cassandraConfig;
    }

    String outputKeyspace(String namespace) {
        if (cassandraConfig.isNamespacesEnabled()) {
            return namespace != null
                ? CharMatcher.is('_').trimLeadingFrom(Names.toAlphanumericAndUnderscore(namespace)) :
                cassandraConfig.getKeyspace();
        } else {
            return cassandraConfig.getKeyspace();
        }
    }

    String outputTable(String streamName) {
        return super.getRawTableName(streamName.toLowerCase()).substring(1);
    }

    String outputTmpTable(String streamName) {
        return super.getTmpTableName(streamName.toLowerCase()).substring(1);
    }

    String outputColumn(String columnName) {
        return Names.doubleQuote(columnName.toLowerCase());
    }

}
