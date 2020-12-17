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

package io.airbyte.scheduler.client;

import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.scheduler.Job;
import java.io.IOException;

/**
 * This client submits a job to the scheduler and then waits for it to complete. It returns the full
 * job object after it has reached a terminal status.
 */
public interface SchedulerJobClient {

  Job createSourceCheckConnectionJob(SourceConnection source, String dockerImage) throws IOException;

  Job createDestinationCheckConnectionJob(DestinationConnection destination, String dockerImage) throws IOException;

  Job createDiscoverSchemaJob(SourceConnection source, String dockerImage) throws IOException;

  Job createGetSpecJob(String dockerImage) throws IOException;

  Job createSyncJob(SourceConnection source,
                    DestinationConnection destination,
                    StandardSync standardSync,
                    String sourceDockerImage,
                    String destinationDockerImage)
      throws IOException;

  Job createResetConnectionJob(
                               DestinationConnection destination,
                               StandardSync standardSync,
                               String destinationDockerImage)
      throws IOException;

}
