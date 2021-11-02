package io.airbyte.integrations.destination.redis;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class RedisOpsProviderTest {

    private RedisOpsProvider redisOpsProvider;

    @BeforeAll
    void setup() {
        var redisContainer = RedisContainerInitializr.initContainer();
        var redisConfig = TestDataFactory.redisConfig(
            redisContainer.getHost(),
            redisContainer.getFirstMappedPort()
        );
        redisOpsProvider = new RedisOpsProvider(redisConfig);
    }

    @AfterEach
    void clean() {
        redisOpsProvider.flush();
    }

    @Test
    void testInsert() {
        assertDoesNotThrow(() -> {
            redisOpsProvider.insert("namespace1", "stream1", "{\"property\":\"data1\"}");
            redisOpsProvider.insert("namespace2", "stream2", "{\"property\":\"data2\"}");
            redisOpsProvider.insert("namespace3", "stream3", "{\"property\":\"data3\"}");
        });
    }

    @Test
    void testGetAll() {
        // given
        redisOpsProvider.insert("namespace", "stream", "{\"property\":\"data1\"}");
        redisOpsProvider.insert("namespace", "stream", "{\"property\":\"data2\"}");

        // when
        var redisRecords = redisOpsProvider.getAll("namespace", "stream");

        // then
        assertThat(redisRecords)
            .isNotNull()
            .hasSize(2)
            .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
            .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"));
    }

    @Test
    void testDelete() {

        // given
        redisOpsProvider.insert("namespace", "stream", "{\"property\":\"data1\"}");
        redisOpsProvider.insert("namespace", "stream", "{\"property\":\"data2\"}");

        // when
        redisOpsProvider.delete("namespace", "stream");
        var redisRecords = redisOpsProvider.getAll("namespace", "stream");

        // then
        assertThat(redisRecords).isEmpty();
    }

    @Test
    void testRename() {
        // given
        redisOpsProvider.insert("namespace", "stream1", "{\"property\":\"data1\"}");
        redisOpsProvider.insert("namespace", "stream1", "{\"property\":\"data2\"}");
        redisOpsProvider.insert("namespace", "stream2", "{\"property\":\"data3\"}");
        redisOpsProvider.insert("namespace", "stream2", "{\"property\":\"data4\"}");

        // when
        redisOpsProvider.rename("namespace", "stream1", "stream2");
        var redisRecords = redisOpsProvider.getAll("namespace", "stream2");


        // then
        assertThat(redisRecords)
            .isNotNull()
            .hasSize(4)
            .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
            .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"))
            .anyMatch(r -> r.getData().equals("{\"property\":\"data3\"}"))
            .anyMatch(r -> r.getData().equals("{\"property\":\"data4\"}"));
    }

}
