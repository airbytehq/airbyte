package io.airbyte.workers.process;

import com.google.common.base.Preconditions;
import io.airbyte.commons.resources.MoreResources;
import io.fabric8.kubernetes.api.model.ContainerStateTerminated;
import io.fabric8.kubernetes.api.model.ContainerStatus;
import io.fabric8.kubernetes.api.model.DeletionPropagation;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.client.KubernetesClient;
import org.apache.commons.io.output.NullOutputStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class KubePodProcess extends Process {
    private static final Logger LOGGER = LoggerFactory.getLogger(KubePodProcess.class);

    private static final int STDIN_REMOTE_PORT = 9001;

    private final KubernetesClient client;
    private final Pod podDefinition;

    private final OutputStream stdin;
    private InputStream stdout;
    private final ServerSocket stdoutServerSocket;
    private final ExecutorService executorService;

    public KubePodProcess(KubernetesClient client, String podName, String image, int stdoutLocalPort, boolean usesStdin) throws IOException, InterruptedException {
        this.client = client;

        // allow reading stdout from pod
        LOGGER.info("Creating socket server...");
        this.stdoutServerSocket = new ServerSocket(stdoutLocalPort);

        executorService = Executors.newSingleThreadExecutor();
        executorService.submit(() -> {
            try {
                LOGGER.info("Creating socket from server...");
                var socket = stdoutServerSocket.accept(); // blocks until connected
                LOGGER.info("Setting stdout...");
                this.stdout = socket.getInputStream();
            } catch (IOException e) {
                e.printStackTrace(); // todo: propagate exception / join at the end of constructor
            }
        });

        // create pod
        var templateResource =  usesStdin ? "kube_queue_poc/pod-io-template.yaml" : "kube_queue_poc/pod-o-template.yaml";
        var template = MoreResources.readResource(templateResource);
        var rendered = template
                .replaceAll("WORKER_IP", InetAddress.getLocalHost().getHostAddress())
                .replaceAll("IMAGE", image)
                .replaceAll("NAME", podName)
                .replaceAll("STDOUT_PORT", String.valueOf(stdoutLocalPort))
                .replaceAll("ENTRYPOINT", KubeProcessBuilderFactoryPOC.getCommandFromImage(image));
        var renderedStream = new ByteArrayInputStream(rendered.getBytes());

        LOGGER.info("Loading pod definition...");
        this.podDefinition = client.pods().load(renderedStream).get();

        LOGGER.info("Creating pod...");
        KubeProcessBuilderFactoryPOC.createIfNotExisting(podName, podDefinition);

        // allow writing stdin to pod
        LOGGER.info("Reading pod IP...");
        var podIp = KubeProcessBuilderFactoryPOC.getPodIP(podName);
        LOGGER.info("Pod IP: {}", podIp);

        if(usesStdin) {
            LOGGER.info("Creating stdin socket...");
            var socketToDestStdIo = new Socket(podIp, STDIN_REMOTE_PORT);
            this.stdin = socketToDestStdIo.getOutputStream();
        } else {
            LOGGER.info("Using null stdin output stream...");
            this.stdin = NullOutputStream.NULL_OUTPUT_STREAM;
        }
    }

    @Override
    public OutputStream getOutputStream() {
        return this.stdin;
    }

    @Override
    public InputStream getInputStream() {
        return this.stdout;
    }

    @Override
    public InputStream getErrorStream() {
        // there is no error stream equivalent for Kube-based processes so we use a null stream here
        return InputStream.nullInputStream();
    }

    @Override
    public int waitFor() throws InterruptedException {
        client.resource(podDefinition).waitUntilCondition(this::allContainersTerminal, 10, TimeUnit.DAYS);
        return exitValue();
    }

    private boolean allContainersTerminal(Pod pod) {
        try {
            for (ContainerStatus containerStatus : pod.getStatus().getContainerStatuses()) {
                if (containerStatus.getState() == null) {
                    return false;
                } else {
                    ContainerStateTerminated terminated = containerStatus.getState().getTerminated();

                    if (terminated == null) {
                        return false;
                    }
                }
            }

            return true;
        } catch(NullPointerException e) {
            return true; // todo: fix this termination handling
        }
    }

    private int getReturnCode(Pod pod) {
        Preconditions.checkArgument(allContainersTerminal(pod));

        int statusCodeSum = 0;

        for (ContainerStatus containerStatus : pod.getStatus().getContainerStatuses()) {
            int statusCode = containerStatus.getState().getTerminated().getExitCode();
            LOGGER.info("Termination status for container " + containerStatus.getName() + "is " + statusCode);
            statusCodeSum += statusCode;
        }

        return statusCodeSum;
    }

    @Override
    public int exitValue() {
        return 0; // todo: fix npes after job has completed
//        Pod refreshedPod = client.resource(podDefinition).get();
//        return getReturnCode(refreshedPod);
    }

    @Override
    public void destroy() {
        try {
            stdoutServerSocket.close();
        } catch (IOException e) {
            throw new RuntimeException(e);
        } finally {
            executorService.shutdown();
            client.resource(podDefinition).withPropagationPolicy(DeletionPropagation.FOREGROUND).delete();
        }
    }
}
