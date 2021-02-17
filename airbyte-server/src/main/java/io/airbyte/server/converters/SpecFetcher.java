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

package io.airbyte.server.converters;

import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workflows.GetSpecWorkflow;
import io.temporal.client.WorkflowClient;

public class SpecFetcher {

    private final WorkflowClient workflowClient;

    public SpecFetcher(WorkflowClient workflowClient) {
        this.workflowClient = workflowClient;
    }

    public ConnectorSpecification execute(String dockerImage) {
        try {
            final GetSpecWorkflow workflow = WorkerUtils.getSpecWorkflow(workflowClient, "fetch-spec-" + dockerImage);
            return workflow.getSpec(dockerImage);
        } catch (Exception e) {
            throw new IllegalArgumentException("no spec output found", e);
        }
    }

}
