package io.airbyte.server.handlers;

import com.google.common.io.MoreFiles;
import com.google.common.io.Resources;
import io.airbyte.commons.resources.MoreResources;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URI;
import java.nio.file.FileSystem;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;

public class OpenApiConfigHandler {
    private static File TMP_FILE;

    static {
        try {
            TMP_FILE = File.createTempFile("airbyte", "openapiconfig");
            TMP_FILE.deleteOnExit();
            Files.writeString(TMP_FILE.toPath(), MoreResources.readResource("openapi/config.yaml"));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public File getFile() {
        return TMP_FILE;
    }
}
