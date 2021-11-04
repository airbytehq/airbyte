package io.airbyte.integrations.destination.redis;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RedisNameTransformerTest {

    private RedisNameTransformer redisNameTransformer;

    @BeforeEach
    void setup() {
        this.redisNameTransformer = new RedisNameTransformer();
    }

    @Test
    void testOutputKey() {

        var table = redisNameTransformer.outputKey("stream_name");

        assertThat(table).matches("_airbyte_raw_stream_name");

    }

    @Test
    void testOutputTmpKey() {

        var table = redisNameTransformer.outputTmpKey("stream_name");

        assertThat(table).matches("_airbyte_tmp_+[a-z]+_stream_name");

    }

    @Test
    void testOutputNamespace() {

        var keyspace = redisNameTransformer.outputNamespace("*keyspace^h");

        assertThat(keyspace).matches("_keyspace_h");

    }

}
