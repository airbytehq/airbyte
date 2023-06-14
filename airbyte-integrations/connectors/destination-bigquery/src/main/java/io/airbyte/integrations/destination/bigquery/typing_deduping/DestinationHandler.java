package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.QuotedStreamId;
import java.util.Optional;

public interface DestinationHandler<DialectTableDefinition> {

  Optional<DialectTableDefinition> findExistingTable(QuotedStreamId id);

  // TODO change this to accept Optional<String>
  void execute(String sql) throws Exception;

}
