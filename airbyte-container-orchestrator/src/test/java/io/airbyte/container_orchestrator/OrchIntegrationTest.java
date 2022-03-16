package io.airbyte.container_orchestrator;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.WorkerHeartbeatServer;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.net.Inet4Address;
import java.net.ServerSocket;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

public class OrchIntegrationTest {
    private static final boolean IS_MINIKUBE = Boolean.parseBoolean(Optional.ofNullable(System.getenv("IS_MINIKUBE")).orElse("false"));

    private static List<Integer> openPorts;
    private static int heartbeatPort;
    private static String heartbeatUrl;
    private static KubernetesClient fabricClient;
    private static KubeProcessFactory processFactory;
    private static final ResourceRequirements DEFAULT_RESOURCE_REQUIREMENTS = new WorkerConfigs(new EnvConfigs()).getResourceRequirements();
    private static final String ENV_KEY = "ENV_VAR_1";
    private static final String ENV_VALUE = "ENV_VALUE_1";
    private static final Map<String, String> ENV_MAP = ImmutableMap.of(ENV_KEY, ENV_VALUE);

    private WorkerHeartbeatServer server;

    @BeforeAll
    public static void init() throws Exception {
        openPorts = new ArrayList<>(getOpenPorts(30)); // todo: should we offer port pairs to prevent deadlock? can create test here with fewer to get
        // this

        heartbeatPort = openPorts.get(0);
        heartbeatUrl = getHost() + ":" + heartbeatPort;

        fabricClient = new DefaultKubernetesClient();

        KubePortManagerSingleton.init(new HashSet<>(openPorts.subList(1, openPorts.size() - 1)));

        final WorkerConfigs workerConfigs = spy(new WorkerConfigs(new EnvConfigs()));
        when(workerConfigs.getEnvMap()).thenReturn(Map.of("ENV_VAR_1", "ENV_VALUE_1"));

        processFactory =
                new KubeProcessFactory(
                        workerConfigs,
                        "default",
                        fabricClient,
                        heartbeatUrl,
                        getHost(),
                        false);
    }

    @Test
    public void test() throws Exception {
        final var envConfigs = new EnvConfigs(Map.of("WORKSPACE_ROOT", "/tmp/workspaces"));
        final var workerConfigs = new WorkerConfigs(envConfigs);
        final var orchestrator = new ReplicationJobOrchestrator(envConfigs, workerConfigs, processFactory);

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

        orchestrator.runJob(
                jobRunConfig,
                syncInput,
                sourceLauncherConfig,
                destinationLauncherConfig
        );
    }

    private static Set<Integer> getOpenPorts(final int count) {
        final Set<ServerSocket> servers = new HashSet<>();
        final Set<Integer> ports = new HashSet<>();

        try {
            for (int i = 0; i < count; i++) {
                final var server = new ServerSocket(0);
                servers.add(server);
                ports.add(server.getLocalPort());
            }
        } catch (final IOException e) {
            throw new RuntimeException(e);
        } finally {
            for (final ServerSocket server : servers) {
                Exceptions.swallow(server::close);
            }
        }

        return ports;
    }


    private static String getHost() {
        try {
            return (IS_MINIKUBE ? Inet4Address.getLocalHost().getHostAddress() : "host.docker.internal");
        } catch (final UnknownHostException e) {
            throw new RuntimeException(e);
        }
    }
}

// todo: this stil runs into port-forwarding problems...
// what is a good way to actually make sure this follows
