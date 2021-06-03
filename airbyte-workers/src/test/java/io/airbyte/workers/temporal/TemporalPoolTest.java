/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers.temporal;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.workers.process.ProcessFactory;
import io.temporal.api.namespace.v1.NamespaceInfo;
import io.temporal.api.workflowservice.v1.DescribeNamespaceResponse;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class TemporalPoolTest {

  @Test
  public void testWaitForTemporalServerOnLogThrowsException() {
    WorkflowServiceStubs workflowServiceStubs = mock(WorkflowServiceStubs.class, Mockito.RETURNS_DEEP_STUBS);
    Path path = mock(Path.class);
    ProcessFactory processFactory = mock(ProcessFactory.class);
    TemporalPool testPool = new TemporalPool(workflowServiceStubs, path, processFactory);
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
