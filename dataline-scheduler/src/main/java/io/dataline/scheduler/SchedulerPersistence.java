/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.scheduler;

import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.JobConfig;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface SchedulerPersistence {

  long createSourceCheckConnectionJob(SourceConnectionImplementation sourceImplementation)
      throws IOException;

  long createDestinationCheckConnectionJob(DestinationConnectionImplementation destinationImplementation)
      throws IOException;

  long createDiscoverSchemaJob(SourceConnectionImplementation sourceImplementation)
      throws IOException;

  long createSyncJob(SourceConnectionImplementation sourceImplementation,
                     DestinationConnectionImplementation destinationImplementation,
                     StandardSync standardSync)
      throws IOException;

  Job getJob(long jobId) throws IOException;

  /**
   * @param configType - type of config, e.g. sync
   * @param configId - id of that config
   * @return lists job in descending order by created_at
   * @throws IOException - what you do when you IO
   */
  List<Job> listJobs(JobConfig.ConfigType configType, String configId) throws IOException;

  Optional<Job> getLastSyncJobForConnectionId(UUID connectionId) throws IOException;

}
