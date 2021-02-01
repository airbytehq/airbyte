package io.airbyte.server.handlers;

import com.google.common.io.Files;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.charset.Charset;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class OpenApiConfigHandlerTest {
    @Test
    public void testGetFile() throws IOException {
        List<String> lines = Files.readLines(new OpenApiConfigHandler().getFile(), Charset.defaultCharset());
        assertTrue(lines.get(0).contains("openapi"));
    }

}