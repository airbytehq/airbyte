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
import io.airbyte.scheduler.models.Job;
import java.io.IOException;

/**
 * Exposes a way of executing short-lived jobs as RPC calls. If it returns successfully, it
 * guarantees a job was submitted. It does not wait for that job to complete. Jobs submitted in by
 * this client are persisted in the Jobs table. It returns the full job object.
 */
public interface SchedulerJobClient {

  Job createOrGetActiveSyncJob(SourceConnection source,
                               DestinationConnection destination,
                               StandardSync standardSync,
                               String sourceDockerImage,
                               String destinationDockerImage)
      throws IOException;

  Job createOrGetActiveResetConnectionJob(DestinationConnection destination,
                                          StandardSync standardSync,
                                          String destinationDockerImage)
      throws IOException;

}
