package io.airbyte.activities;

import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.GetSpecWorker;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.kubernetes.client.proto.V1Batch;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Random;

public class GetSpecActivityImpl implements GetSpecActivity {


    private final Path workspaceRoot;
    private final ProcessBuilderFactory pbf;

    public GetSpecActivityImpl(Path workspaceRoot, ProcessBuilderFactory pbf) {
        this.workspaceRoot = workspaceRoot;
        this.pbf = pbf;
    }

    @Override
    public ConnectorSpecification run(String dockerImage) throws Exception {
        final long jobId = new Random().nextLong();
        final int attempt = 0;
        final IntegrationLauncher launcher =  new AirbyteIntegrationLauncher(jobId, attempt, dockerImage, pbf);
        final Path jobRoot = workspaceRoot.resolve(String.valueOf(jobId)).resolve(String.valueOf(attempt));

        Files.createDirectories(jobRoot);

        GetSpecWorker worker = new DefaultGetSpecWorker(launcher);

        return worker.run(new JobGetSpecConfig().withDockerImage(dockerImage), jobRoot)
                .getOutput()
                .get()
                .getSpecification();
    }
}