package io.airbyte.integrations.destination.jdbc;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import java.util.UUID;

public class CreateDropTableOperation {

  public final void attempt(final String outputSchema,
      final JdbcDatabase database,
      final NamingConventionTransformer namingResolver,
      final SqlOperations sqlOps) throws Exception {

    // verify we have write permissions on the target schema by creating a table with a random name,
    // then dropping that table
    final String outputTableName = namingResolver.getIdentifier("_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", ""));
    sqlOps.createSchemaIfNotExists(database, outputSchema);
    sqlOps.createTableIfNotExists(database, outputSchema, outputTableName);
    sqlOps.dropTableIfExists(database, outputSchema, outputTableName);
  }

}
