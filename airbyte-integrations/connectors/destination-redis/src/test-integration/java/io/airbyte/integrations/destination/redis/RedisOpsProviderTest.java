package io.airbyte.integrations.destination.redis;

import java.util.Map;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import redis.clients.jedis.JedisPool;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class RedisOpsProviderTest {

    private RedisContainerInitializr.RedisContainer redisContainer;

    private JedisPool jedisPool;

    @BeforeAll
    void setup() {
        redisContainer = RedisContainerInitializr.initContainer();
        this.jedisPool = new JedisPool(redisContainer.getHost(), redisContainer.getFirstMappedPort());
    }

    @Test
    void test() {

        var jedis = jedisPool.getResource();
        var key = generateIncrKey("namespace", "stream");

        var incr1 = jedis.incr(key);
        jedis.hmset(generateKey("namespace", "stream", incr1), Map.of("f1", "v1"));
        var incr2 = jedis.incr(key);
        jedis.hmset(generateKey("namespace", "stream", incr2), Map.of("f2", "v2"));
        var incr3 = jedis.incr(key);
        jedis.hmset(generateKey("namespace", "stream", incr3), Map.of("f2", "v2"));
        var incr4 = jedis.incr(key);
        jedis.hmset(generateKey("namespace", "stream", incr4), Map.of("f2", "v2"));
        var incr5 = jedis.incr(key);
        jedis.hmset(generateKey("namespace", "stream", incr5), Map.of("f2", "v2"));
        var incr6 = jedis.incr(key);
        jedis.hmset(generateKey("namespace", "stream", incr6), Map.of("f2", "v2"));
        var incr7 = jedis.incr(key);
        jedis.hmset(generateKey("namespace", "stream", incr7), Map.of("f2", "v2"));
        var incr8 = jedis.incr(key);
        jedis.hmset(generateKey("namespace", "stream", incr8), Map.of("f2", "v2"));
        var incr9 = jedis.incr(key);
        jedis.hmset(generateKey("namespace", "stream", incr9), Map.of("f2", "v2"));
        var incr10 = jedis.incr(key);
        jedis.hmset(generateKey("namespace", "stream", incr10), Map.of("f2", "v2"));

        var keys = jedis.keys( "namespace:stream:[0-9]*").stream()
            //.filter(k -> !k.contains("incr"))
            .collect(Collectors.toList());

        keys.forEach(System.out::println);

        keys.stream().map(jedis::hgetAll).forEach(System.out::println);

        jedis.set(key, "0");
        System.out.println("VALUE: " + jedis.get(key));
        jedis.incr(key);
        System.out.println("VALUE2: " + jedis.get(key));

    }

    private String generateIncrKey(String namespace, String stream) {
        return namespace + ":" + stream + ":" + "incr";
    }

    private String generateKey(String namespace, String stream, Long id) {
        return namespace + ":" + stream + ":" + id;
    }

}
