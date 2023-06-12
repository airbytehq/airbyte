package io.airbyte.integrations.destination.bigquery.typing_deduping;

import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.QuotedStreamId;
import java.util.Optional;

public interface DestinationInteractorThing<DialectTableDefinition> {

  Optional<DialectTableDefinition> findExistingTable(QuotedStreamId id);

  void execute(String sql) throws Exception;

}
