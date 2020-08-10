package io.dataline.conduit.commons.db;

import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.sql.SQLException;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class TestClientUuid {
    @Test
    void testUuidFormat() throws SQLException, IOException {
        DatabaseHelper.initializeDatabase();
        String uuid = ClientUuid.get();
        assertTrue(uuid.matches("/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/"));
    }

    @Test
    void testSameUuidOverInitializations() throws SQLException, IOException {
        DatabaseHelper.initializeDatabase();
        String uuid1 = ClientUuid.get();

        DatabaseHelper.initializeDatabase();
        String uuid2 = ClientUuid.get();

        assertEquals(uuid1, uuid2);
    }
}
