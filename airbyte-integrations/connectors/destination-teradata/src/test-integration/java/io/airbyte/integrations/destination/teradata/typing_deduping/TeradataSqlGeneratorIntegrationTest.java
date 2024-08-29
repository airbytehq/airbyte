package io.airbyte.integrations.destination.teradata.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.*;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.integrations.destination.teradata.TeradataDestination;
import io.airbyte.integrations.destination.teradata.TeradataNameTransformer;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.Name;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;

import javax.sql.DataSource;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import static io.airbyte.integrations.destination.teradata.typing_deduping.TeradataSqlGenerator.JSON_TYPE;
import static org.junit.jupiter.api.Assertions.*;

/**
 Standard-tests class for the SqlGenerator class (create table and update/copy their content) part of the destination V2 interface.
 See TeradataSqlGenerator.java for the implementation.

 TODO: use "extend JdbcTypingDedupingTest" and use MysqlTypingDedupingTest.kt as inspiration source for testing
*/
@Execution(ExecutionMode.SAME_THREAD)
public class TeradataSqlGeneratorIntegrationTest extends JdbcSqlGeneratorIntegrationTest<MinimumDestinationState> {

    private static JdbcDatabase database;
    private static String databaseName;


    @BeforeAll
    public static void setupTeradata() throws IOException {
        final TeradataDestination teradataDestination = new TeradataDestination();
        final DataSource dataSource = teradataDestination.getDataSource(Jsons.deserialize(Files.readString(Paths.get("secrets/config.json"))));
        databaseName = "HR";
        database = new DefaultJdbcDatabase(dataSource);
    }

    @NotNull
    @Override
    protected JdbcDatabase getDatabase() {
        return database;
    }

    @NotNull
    @Override
    protected DataType<?> getStructType() {
        return JSON_TYPE;
    }

    @NotNull
    @Override
    protected JdbcSqlGenerator getSqlGenerator() {
        return new TeradataSqlGenerator(new TeradataNameTransformer(), false);
    }

    @Nullable
    @Override
    protected SQLDialect getSqlDialect() {
        return SQLDialect.DEFAULT;
    }

    @Nullable
    @Override
    protected Field<?> toJsonValue(@Nullable String s) {
        return DSL.cast(DSL.val(s), JSON_TYPE);
    }

    @NotNull
    @Override
    protected DestinationHandler<MinimumDestinationState> getDestinationHandler() {
        return new TeradataDestinationHandler(databaseName, database, getNamespace());
    }

    @Override
    protected boolean getSupportsSafeCast() {
        return true;
    }

    @Override
    protected void createNamespace(String namespace) throws SQLException {
        database.execute(connection -> connection.createStatement().execute(String.format("CREATE DATABASE \"%s\" AS PERMANENT = 120e6, SPOOL = 120e6;", namespace)));
    }

    @Override
    protected void teardownNamespace(@NotNull String namespace) throws SQLException {
        database.execute(connection -> {
            var statment = connection.createStatement();

            statment.execute(String.format("DELETE DATABASE \"%s\";", namespace));
            statment.execute(String.format("DROP DATABASE \"%s\";", namespace));
        });
    }

//    @Test
//    void test() throws SQLException {
//        database.execute( connection -> {
//            var statement = connection.createStatement();
//            statement.execute("SELECT DatabaseName FROM DBC.DatabasesV WHERE DatabaseName LIKE '%sql_generator%';");
//
//            List<String> databaseNames = new ArrayList<>();
//            while (statement.getResultSet().next()) {
//                String databaseName = statement.getResultSet().getString("DatabaseName");
//                databaseNames.add(databaseName);
//            }
//
//            statement.close();
//
//            for (String databaseName : databaseNames) {
//                var innerstatement = connection.createStatement();
//                try {
//                    innerstatement.execute(String.format("DELETE DATABASE \"%s\";", databaseName));
//                    innerstatement.execute(String.format("DROP DATABASE \"%s\";", databaseName));
//                    innerstatement.close();
//                    System.out.println("Dropped database: " + databaseName);
//                } catch (SQLException e) {
//                    System.out.println("Failed to drop database: " + databaseName);
//                }
//
//            }
//        });
//    }

    @Override
    public void testCreateTableIncremental() throws Exception {
        final Sql sql = getGenerator().createTable(getIncrementalDedupStream(), "", false);
        getDestinationHandler().execute(sql);

        List<DestinationInitialStatus<MinimumDestinationState>> initialStatuses = getDestinationHandler().gatherInitialState(List.of(getIncrementalDedupStream()));
        assertEquals(1, initialStatuses.size());
        final DestinationInitialStatus<MinimumDestinationState> initialStatus = initialStatuses.getFirst();
        assertTrue(initialStatus.isFinalTablePresent());
        assertFalse(initialStatus.isSchemaMismatch());
    } //

//    @Override
//    public List<JsonNode> dumpFinalTableRecords(StreamId streamId, String suffix) throws Exception {
//        String TableName = streamId.getFinalNamespace() + "." + streamId.getFinalName() + suffix;
//        return database.queryJsons("SELECT * FROM " + TableName);
//    }


    @Override
    public void insertRecords(Name tableName, List<String> columnNames, List<? extends JsonNode> records, String... columnsToParseJson) throws SQLException {
        String sqlStatment = records.stream()
                .map(record -> {

                    List<String> result = columnNames.stream().map(fieldName -> {
                        var column = record.get(fieldName);
                        String columnAsString;
                        if(column == null) {
                            columnAsString = null;
                        } else if (column.isTextual()) {
                            columnAsString = column.asText();
                        } else {
                            columnAsString = column.toString();
                        }

                        if (Arrays.asList(columnsToParseJson).contains(fieldName)) {
                            return toJsonValue(columnAsString).toString();
                        } else if (columnAsString == null) {
                            return null;
                        } else {
                            return "'" + columnAsString + "'";
                        }
                    }).toList();

                    List<String> wrappedColumnNames = columnNames.stream().map(columnName -> '"' + columnName + '"').toList();


                    return "INSERT INTO " + tableName + " (" +String.join(",", wrappedColumnNames) + ") values (" + String.join(",", result) + ");";
                })
                .collect(Collectors.joining("\n"));

        database.execute(sqlStatment);
    }


}
