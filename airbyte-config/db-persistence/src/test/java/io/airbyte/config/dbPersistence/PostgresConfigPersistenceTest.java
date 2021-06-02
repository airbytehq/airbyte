package io.airbyte.config.dbPersistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

import com.google.common.collect.Sets;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class PostgresConfigPersistenceTest {
    public static final UUID UUID_1 = new UUID(0, 1);
    public static final StandardSourceDefinition SOURCE_1 = new StandardSourceDefinition();

    static {
        SOURCE_1.withSourceDefinitionId(UUID_1)
                .withName("apache storm");
    }

    public static final UUID UUID_2 = new UUID(0, 2);
    public static final StandardSourceDefinition SOURCE_2 = new StandardSourceDefinition();
    private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");

    static {
        SOURCE_2.withSourceDefinitionId(UUID_2)
                .withName("apache storm");
    }

    private Path rootPath;
    private JsonSchemaValidator schemaValidator;

    private DefaultConfigPersistence configPersistence;

    @BeforeEach
    void setUp() throws IOException {
        schemaValidator = mock(JsonSchemaValidator.class);
        rootPath = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), DefaultConfigPersistenceTest.class.getName());

        configPersistence = new DefaultConfigPersistence(rootPath, schemaValidator);
    }

    @Test
    void testReadWriteConfig() throws IOException, JsonValidationException, ConfigNotFoundException {
        configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), SOURCE_1);

        assertEquals(
                SOURCE_1,
                configPersistence.getConfig(
                        ConfigSchema.STANDARD_SOURCE_DEFINITION,
                        UUID_1.toString(),
                        StandardSourceDefinition.class));
    }

    @Test
    void testListConfigs() throws JsonValidationException, IOException {
        configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), SOURCE_1);
        configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_2.toString(), SOURCE_2);

        assertEquals(
                Sets.newHashSet(SOURCE_1, SOURCE_2),
                Sets.newHashSet(configPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)));
    }

    @Test
    void writeConfigWithJsonSchemaRef() throws JsonValidationException, IOException, ConfigNotFoundException {
        final StandardSync standardSync = new StandardSync()
                .withName("sync")
                .withPrefix("sync")
                .withConnectionId(UUID_1)
                .withSourceId(UUID.randomUUID())
                .withDestinationId(UUID.randomUUID())
                .withOperationIds(List.of(UUID.randomUUID()));

        configPersistence.writeConfig(ConfigSchema.STANDARD_SYNC, UUID_1.toString(), standardSync);

        assertEquals(
                standardSync,
                configPersistence.getConfig(ConfigSchema.STANDARD_SYNC, UUID_1.toString(), StandardSync.class));
    }

    @Test
    void writeConfigInvalidConfig() throws JsonValidationException {
        StandardSourceDefinition standardSourceDefinition = SOURCE_1.withName(null);

        doThrow(new JsonValidationException("error")).when(schemaValidator).ensure(any(), any());

        assertThrows(JsonValidationException.class, () -> configPersistence.writeConfig(
                ConfigSchema.STANDARD_SOURCE_DEFINITION,
                UUID_1.toString(),
                standardSourceDefinition));
    }

}