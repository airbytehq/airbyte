package io.airbyte.integrations.destination.cassandra;

/*import static io.airbyte.integrations.destination.cassandra.TestDataFactory.createAirbyteStream;
import static io.airbyte.integrations.destination.cassandra.TestDataFactory.createConfiguredAirbyteCatalog;
import static io.airbyte.integrations.destination.cassandra.TestDataFactory.createConfiguredAirbyteStream;*/
import static org.mockito.Mockito.mock;

import io.airbyte.protocol.models.DestinationSyncMode;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.platform.commons.util.ReflectionUtils;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CassandraMessageConsumerTest {

    private static final String AIRBYTE_NAMESPACE_1 = "airbyte_namespace_1";
    private static final String AIRBYTE_NAMESPACE_2 = "airbyte_namespace_2";

    private static final String AIRBYTE_STREAM_1 = "airbyte_stream_1";
    private static final String AIRBYTE_STREAM_2 = "airbyte_stream_2";

    private CassandraMessageConsumer cassandraMessageConsumer;

    private final CassandraCqlProvider cqlProvider = mock(CassandraCqlProvider.class);

    @BeforeAll
    void setup() throws NoSuchFieldException, IllegalAccessException {
        /*var cassandraConfig = TestDataFactory.createCassandraConfig(
            "usr",
            "pw",
            "127.0.0.1",
            8080
        );

        var stream1 = createAirbyteStream(AIRBYTE_STREAM_1, AIRBYTE_NAMESPACE_1);
        var stream2 = createAirbyteStream(AIRBYTE_STREAM_2, AIRBYTE_NAMESPACE_2);

        var cStream1 = createConfiguredAirbyteStream(DestinationSyncMode.APPEND, stream1);
        var cStream2 = createConfiguredAirbyteStream(DestinationSyncMode.OVERWRITE, stream2);

        var catalog = createConfiguredAirbyteCatalog(cStream1, cStream2);

        var fieldr = ReflectionUtils.findFields(CassandraMessageConsumer.class, f -> f.getType() == CassandraCqlProvider.class,
            ReflectionUtils.HierarchyTraversalMode.TOP_DOWN);


        cassandraMessageConsumer = new CassandraMessageConsumer(cassandraConfig, catalog, (message) -> {});

        var field = cassandraMessageConsumer.getClass().getDeclaredField("cassandraCqlProvider");
        field.setAccessible(true);
        field.set(cassandraMessageConsumer, cqlProvider);*/

    }

    @Test
    void test() {

    }

}
