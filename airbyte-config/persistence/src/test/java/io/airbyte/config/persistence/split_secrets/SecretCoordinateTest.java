package io.airbyte.config.persistence.split_secrets;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class SecretCoordinateTest {

    @Test
    void testToString() {
        final var coordinate = new SecretCoordinate("some_base", 1);
        assertEquals("some_base_v1", coordinate.toString());
    }
}