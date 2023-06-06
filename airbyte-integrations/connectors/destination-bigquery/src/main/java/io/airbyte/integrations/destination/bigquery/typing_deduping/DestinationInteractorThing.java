package io.airbyte.integrations.destination.bigquery.typing_deduping;

import java.util.Optional;

public interface DestinationInteractorThing<DialectTableDefinition> {

  Optional<DialectTableDefinition> findExistingTable(String namespace, String name);

  void execute(String sql) throws Exception;

}
