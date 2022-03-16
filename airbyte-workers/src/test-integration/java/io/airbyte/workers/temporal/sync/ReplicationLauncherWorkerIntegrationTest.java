package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.storage.CloudStorageConfigs;
import io.airbyte.config.storage.MinioS3ClientFactory;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.process.AsyncOrchestratorPodProcess;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.storage.DocumentStoreClient;
import io.airbyte.workers.storage.S3DocumentStoreClient;
import io.fabric8.kubernetes.api.model.ContainerBuilder;
import io.fabric8.kubernetes.api.model.ContainerPort;
import io.fabric8.kubernetes.api.model.EnvVar;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import software.amazon.awssdk.services.s3.model.CreateBucketRequest;

import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class ReplicationLauncherWorkerIntegrationTest {

    private static KubernetesClient fabricClient;
    private static DocumentStoreClient documentStoreClient;
    private static Process portForwardProcess;

    @BeforeAll
    public static void init() throws Exception {
        fabricClient = new DefaultKubernetesClient();

        final var podName = "test-minio-" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

        final var minioContainer = new ContainerBuilder()
                .withName("minio")
                .withImage("minio/minio:latest")
                .withArgs("server", "/home/shared")
                .withEnv(
                        new EnvVar("MINIO_ACCESS_KEY", "minio", null),
                        new EnvVar("MINIO_SECRET_KEY", "minio123", null))
                .withPorts(new ContainerPort(9000, null, null, null, null))
                .build();

        final Pod minioPod = new PodBuilder()
                .withApiVersion("v1")
                .withNewMetadata()
                .withName(podName)
                .withNamespace("default")
                .endMetadata()
                .withNewSpec()
                .withRestartPolicy("Never")
                .withContainers(minioContainer)
                .endSpec()
                .build();

        fabricClient.pods().inNamespace("default").create(minioPod);
        fabricClient.resource(minioPod).waitUntilReady(1, TimeUnit.MINUTES);

        portForwardProcess = new ProcessBuilder("kubectl", "port-forward", "pod/" + podName, "9432:9000").start();

        Thread.sleep(5000);

        final var localMinioEndpoint = "http://localhost:9432";

        final var minioConfig = new CloudStorageConfigs.MinioConfig(
                "anything",
                "minio",
                "minio123",
                localMinioEndpoint);

        final var s3Client = new MinioS3ClientFactory(minioConfig).get();

        final var createBucketRequest = CreateBucketRequest.builder()
                .bucket("anything")
                .build();

        s3Client.createBucket(createBucketRequest);

        documentStoreClient = S3DocumentStoreClient.minio(
                minioConfig,
                Path.of("/"));
    }

    @Test
    public void test() throws WorkerException {
        final var jobRoot = Path.of("/tmp/jobRoot");
        final var jobId = "0";
        final var attemptId = 0L;

        final JobRunConfig jobRunConfig = new JobRunConfig().withJobId(jobId).withAttemptId(attemptId);

        final StandardSyncInput syncInput = new StandardSyncInput()
                .withSourceConfiguration(Jsons.deserialize("""
                    { "pokemon_name": "ditto" }
                    """))
                .withDestinationConfiguration(Jsons.deserialize("""
                    { "destination_path": "somepath" }
                    """))
                .withNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType.SOURCE)
                .withNamespaceFormat(null)
                .withPrefix("prefix-")
                .withCatalog(new ConfiguredAirbyteCatalog().withStreams(List.of(new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("pokemon")).withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.APPEND))));

        final IntegrationLauncherConfig sourceLauncherConfig = new IntegrationLauncherConfig()
                .withAttemptId(attemptId)
                .withJobId(jobId)
                .withDockerImage("airbyte/source-pokeapi:0.1.4");

        final IntegrationLauncherConfig destinationLauncherConfig = new IntegrationLauncherConfig()
                .withAttemptId(attemptId)
                .withJobId(jobId)
                .withDockerImage("airbyte/destination-local-json:0.2.10");

        final var connectionId = UUID.randomUUID();

       final var orchestratorConfig = new WorkerApp.ContainerOrchestratorConfig(
                "default",
               documentStoreClient,
                fabricClient,
                null,
                null,
                "airbyte/container-orchestrator:dev",
                null);

        final var worker = new ReplicationLauncherWorker(
                connectionId,
                orchestratorConfig,
                sourceLauncherConfig,
                destinationLauncherConfig,
                jobRunConfig,
                null
        );

        worker.run(syncInput, jobRoot);
    }

    @AfterAll
    public static void teardown() throws InterruptedException {
        Thread.sleep(30000);
        try {
            portForwardProcess.destroyForcibly();
        } catch (Exception e) {
            e.printStackTrace();
        }

        try {
            fabricClient.pods().delete();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}

// todo: necessary env vars aren't transferred like WORKSPACE_ROOT
