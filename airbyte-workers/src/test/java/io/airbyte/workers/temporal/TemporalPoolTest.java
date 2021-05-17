package io.airbyte.workers.temporal;

import io.airbyte.workers.process.ProcessBuilderFactory;
import io.temporal.api.namespace.v1.NamespaceInfo;
import io.temporal.api.workflowservice.v1.DescribeNamespaceResponse;
import io.temporal.serviceclient.WorkflowServiceStubs;
import org.apache.commons.compress.utils.Lists;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class TemporalPoolTest {
    @Test
    public void testWaitForTemporalServerOnLogThrowsException() {
        WorkflowServiceStubs workflowServiceStubs = mock(WorkflowServiceStubs.class, Mockito.RETURNS_DEEP_STUBS);
        Path path = mock(Path.class);
        ProcessBuilderFactory processBuilderFactory = mock(ProcessBuilderFactory.class);
        TemporalPool testPool = new TemporalPool(workflowServiceStubs, path, processBuilderFactory);
        DescribeNamespaceResponse describeNamespaceResponse = mock(DescribeNamespaceResponse.class);
        NamespaceInfo namespaceInfo = mock(NamespaceInfo.class);

        when(namespaceInfo.getName()).thenReturn("default");
        when(describeNamespaceResponse.getNamespaceInfo()).thenReturn(namespaceInfo);
        when(workflowServiceStubs.blockingStub().listNamespaces(any()).getNamespacesList())
                .thenThrow(RuntimeException.class)
                .thenReturn(List.of(describeNamespaceResponse));
        testPool.waitForTemporalServerAndLog();
    }
}