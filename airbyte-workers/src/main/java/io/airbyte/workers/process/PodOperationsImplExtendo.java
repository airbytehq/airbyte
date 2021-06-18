package io.airbyte.workers.process;

import io.fabric8.kubernetes.client.Config;
import io.fabric8.kubernetes.client.dsl.internal.core.v1.PodOperationsImpl;
import okhttp3.OkHttpClient;

public class PodOperationsImplExtendo extends PodOperationsImpl {
    public PodOperationsImplExtendo(OkHttpClient client, Config config) {
        super(client, config);
    }
}
