package io.airbyte.workers.process;

import io.airbyte.workers.storage.DocumentStoreClient;
import io.fabric8.kubernetes.api.model.ContainerBuilder;
import io.fabric8.kubernetes.api.model.ContainerPort;
import io.fabric8.kubernetes.api.model.EnvVar;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.api.model.PodBuilder;
import io.fabric8.kubernetes.api.model.Volume;
import io.fabric8.kubernetes.api.model.VolumeBuilder;
import io.fabric8.kubernetes.api.model.VolumeMount;
import io.fabric8.kubernetes.api.model.VolumeMountBuilder;
import io.fabric8.kubernetes.client.KubernetesClient;
import lombok.extern.slf4j.Slf4j;

import java.util.Optional;
import java.util.concurrent.TimeUnit;

// todo: create async docker process w/ integration test
@Slf4j
public class AsyncKubePodProcess implements KubePod {

    /**
     * possible states:
     * not_started (pending, pod could be in Error, unschedulable, etc) <-- should track how long this is in pending
     * initializing (on-start started but not completed)
     * done_initializing (on-start completed)
     * running (main started)
     * done_running (main ended)
     * failed (main or on-start failed -- set by on-complete)
     * succeeded (both main and on-start succeeded -- set by on-complete)
     *
     * how to handle false starts? --> when checking for this state change, also look for existence of actual pod
     * how to handle undetected failures? --> make sure to handle pod deletes properly
     */

    private final KubePodInfo kubePodInfo;
    private final DocumentStoreClient documentStoreClient;
    private final KubernetesClient kubernetesClient;

    public AsyncKubePodProcess(
            final KubePodInfo kubePodInfo,
            final DocumentStoreClient documentStoreClient,
            final KubernetesClient kubernetesClient) {
        this.kubePodInfo = kubePodInfo;
        this.documentStoreClient = documentStoreClient;
        this.kubernetesClient = kubernetesClient;
    }

    public Optional<String> getOutput() {
        return documentStoreClient.read(getInfo().namespace() + "/" + getInfo().name() + "/output");
    }

    @Override
    public int exitValue() {
        final var optionalExitValue = documentStoreClient.read(getInfo().namespace() + "/" + getInfo().name() + "/exit-value");

        if(optionalExitValue.isPresent()) {
            return Integer.parseInt(optionalExitValue.get());
        } else {
            throw new IllegalThreadStateException("Exit value isn't available yet on the document store.");
        }
    }

    @Override
    public void destroy() {
        final var wasDestroyed = kubernetesClient.pods()
                .inNamespace(getInfo().namespace())
                .withName(getInfo().name())
                .delete();

        if(wasDestroyed) {
            log.info("Deleted pod {} in namespace {}", getInfo().name(), getInfo().namespace());
        } else {
            log.warn("Wasn't able to delete pod {} from namespace {}", getInfo().name(), getInfo().namespace());
        }
    }

    @Override
    public boolean waitFor(long timeout, TimeUnit unit) throws InterruptedException {
        return false; // todo
    }

    @Override
    public int waitFor() throws InterruptedException {
        return 0; // todo
    }

    @Override
    public KubePodInfo getInfo() {
        return kubePodInfo;
    }

    // todo: should this check if it is already created? or just expect it to fail if called twice
    // todo: will need arguments that allow creating with custom options + ability to log + access document store
    // todo: resource requirements
    public void create() {
        final Volume configVolume = new VolumeBuilder()
                .withName("airbyte-config")
                .withNewEmptyDir()
                .withMedium("Memory")
                .endEmptyDir()
                .build();

        final VolumeMount configVolumeMount = new VolumeMountBuilder()
                .withName("airbyte-config")
                .withMountPath("/config") // todo: magic string
                .build();

        // don't use init container so main container can start to load simultaneously
        final var onStartContainer =  new ContainerBuilder()
                .withName("on-start")
                .withImage("curlimages/curl:7.80.0")
                .withArgs("server", "/home/shared")
                .withEnv(
                        new EnvVar("MINIO_ACCESS_KEY", "minio", null),
                        new EnvVar("MINIO_SECRET_KEY", "minio123", null))
                .withPorts(new ContainerPort(9000, null, null, null, null))
                .withVolumeMounts(configVolumeMount)
                .build();

        // todo: allow launching own pods
        final var mainContainer =  new ContainerBuilder()
                .withName("minio")
                .withImage("minio/minio:latest")
                .withArgs("server", "/home/shared")
                .withEnv(
                        new EnvVar("MINIO_ACCESS_KEY", "minio", null),
                        new EnvVar("MINIO_SECRET_KEY", "minio123", null))
                .withPorts(new ContainerPort(9000, null, null, null, null))
                .withVolumeMounts(configVolumeMount)
                .build();

        final var onCompleteContainer =  new ContainerBuilder()
                .withName("on-complete")
                .withImage("curlimages/curl:7.80.0")
                .withArgs("server", "/home/shared")
                .withEnv(
                        new EnvVar("MINIO_ACCESS_KEY", "minio", null),
                        new EnvVar("MINIO_SECRET_KEY", "minio123", null))
                .withPorts(new ContainerPort(9000, null, null, null, null))
                .withVolumeMounts(configVolumeMount)
                .build();

        // todo: configure logging, allow injecting misc info like pull policies and such
        final Pod pod = new PodBuilder()
                .withApiVersion("v1")
                .withNewMetadata()
                .withName(getInfo().name())
                .withNamespace(getInfo().namespace())
                .endMetadata()
                .withNewSpec()
                .withRestartPolicy("Never")
                .withContainers(onStartContainer, mainContainer, onCompleteContainer)
                .endSpec()
                .build();

        // todo: create shared in-memory volume

        kubernetesClient.pods().create(pod);
    }
}
