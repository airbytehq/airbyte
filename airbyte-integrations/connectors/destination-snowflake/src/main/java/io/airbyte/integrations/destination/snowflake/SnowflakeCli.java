package io.airbyte.integrations.destination.snowflake;

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.sql.DatabaseMetaData;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;
import org.apache.commons.lang3.tuple.Pair;

public class SnowflakeCli {

  public static void main(final String[] args) throws Exception {
    if (args.length < 3 || args.length % 2 != 1) {
      System.out.println("Usage: java -jar whatever.jar <postgres-config> <schema1> <table1> [<schema2> <table2> ...]");
      System.exit(1);
    }

    final String configStr = args[0];
    final List<Pair<String, String>> tables = new ArrayList<>();
    for (int i = 1; i < args.length; i += 2){
      tables.add(Pair.of(args[i], args[i + 1]));
    }

    final SnowflakeInternalStagingDestination destination = new SnowflakeInternalStagingDestination(OssCloudEnvVarConsts.AIRBYTE_CLOUD);
    final JdbcDatabase database = destination.getDatabase(destination.getDataSource(Jsons.deserialize(configStr)));
    final SnowflakeSqlOperations ops = new SnowflakeSqlOperations();

    // Check table existence
    boolean allTablesExist = true;
    final DatabaseMetaData dbm = database.getMetaData();
    for (final Pair<String, String> tableIdentifier : tables) {
      final ResultSet tableList = dbm.getTables(null, tableIdentifier.getLeft(), tableIdentifier.getRight(), null);
      if (!tableList.next()) {
        System.out.println("Table does not exist: " + tableIdentifier);
        allTablesExist = false;
      }
    }
    if (!allTablesExist) {
      System.exit(1);
    }

    System.out.println("All tables found to exist; dropping them now.");
    for (final Pair<String, String> tableIdentifier : tables) {
      System.out.println("Dropping " + tableIdentifier);
      ops.dropTableIfExists(database, tableIdentifier.getLeft(), tableIdentifier.getRight());
    }
  }
}
