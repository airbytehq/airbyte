
package io.airbyte.integrations.source.vertica;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.sql.SQLException;
import java.sql.ResultSet;
import static io.airbyte.db.jdbc.DateTimeConverter.putJavaSQLTime;

public class VerticaSourceOperations  extends JdbcSourceOperations {
    private static final Logger LOGGER = LoggerFactory.getLogger(VerticaSourceOperations.class);
    @Override
    protected void putTime(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
        putJavaSQLTime(node, columnName, resultSet, index);
    }
}