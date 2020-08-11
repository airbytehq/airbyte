package io.dataline.commons.db;

import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.sql.SQLException;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

public class TestDatabaseHelper {
    @Test
    void testTableCreation() throws SQLException, IOException {
        int numTables = DatabaseHelper.countTables();
        assertEquals(0, numTables);

        DatabaseHelper.initializeDatabase();

        numTables = DatabaseHelper.countTables();
        assertNotEquals(0, numTables);
    }
}
