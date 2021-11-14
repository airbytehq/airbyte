package io.airbyte.integrations.destination.redis;

public class RedisCacheFactory {

    private RedisCacheFactory() {

    }

    static RedisCache newInstance(RedisConfig redisConfig) {
        return switch (redisConfig.getCacheType()) {
            case HASH -> new RedisHCache(redisConfig);
        };
    }

}
