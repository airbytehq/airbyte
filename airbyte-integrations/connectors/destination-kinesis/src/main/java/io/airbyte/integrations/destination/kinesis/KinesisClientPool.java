package io.airbyte.integrations.destination.kinesis;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import software.amazon.awssdk.services.kinesis.KinesisClient;

public class KinesisClientPool {

    private static final ConcurrentHashMap<KinesisConfig, Tuple<KinesisClient, AtomicInteger>> clients;

    static {
        clients = new ConcurrentHashMap<>();
    }

    private KinesisClientPool() {

    }

    public static KinesisClient initClient(KinesisConfig kinesisConfig) {
        var cachedClient = clients.get(kinesisConfig);
        if (cachedClient != null) {
            cachedClient.value2().incrementAndGet();
            return cachedClient.value1();
        } else {
            var client = KinesisUtils.buildKinesisClient(kinesisConfig);
            clients.put(kinesisConfig, Tuple.of(client, new AtomicInteger(1)));
            return client;
        }
    }

    public static void closeClient(KinesisConfig kinesisConfig) {
        var cachedClient = clients.get(kinesisConfig);
        if (cachedClient == null) {
            throw new IllegalStateException("No session for the provided config");
        }
        int count = cachedClient.value2().decrementAndGet();
        if (count < 1) {
            cachedClient.value1().close();
            clients.remove(kinesisConfig);
        }
    }
}
