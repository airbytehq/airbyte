package io.airbyte.activities;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.workers.DefaultDiscoverCatalogWorker;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.DiscoverCatalogWorker;
import io.airbyte.workers.GetSpecWorker;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Random;

public class DiscoverCatalogActivityImpl implements  DiscoverCatalogActivity {
    private final Path workspaceRoot;
    private final ProcessBuilderFactory pbf;

    public DiscoverCatalogActivityImpl(Path workspaceRoot, ProcessBuilderFactory pbf) {
        this.workspaceRoot = workspaceRoot;
        this.pbf = pbf;
    }

    @Override
    public AirbyteCatalog discoverCatalog(String dockerImage, JsonNode connectionConfig) throws IOException {
        final long jobId = new Random().nextLong();
        final int attempt = 0;
        final IntegrationLauncher launcher =  new AirbyteIntegrationLauncher(jobId, attempt, dockerImage, pbf);
        final Path jobRoot = workspaceRoot.resolve(String.valueOf(jobId)).resolve(String.valueOf(attempt));

        Files.createDirectories(jobRoot);

        DiscoverCatalogWorker worker = new DefaultDiscoverCatalogWorker(launcher);

        return worker.run(new StandardDiscoverCatalogInput().withConnectionConfiguration(connectionConfig), jobRoot)
                .getOutput()
                .get()
                .getCatalog();
    }
}
