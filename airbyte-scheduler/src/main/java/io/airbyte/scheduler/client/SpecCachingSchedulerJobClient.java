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

import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This client caches only the results of spec jobs as their output should not change (except in the
 * case where the docker image is replaced with an image of the same name and tag) and they are
 * called very frequently.
 */
public class SpecCachingSchedulerJobClient extends DefaultSchedulerJobClient implements CachingSchedulerJobClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(SpecCachingSchedulerJobClient.class);

  private final Cache<String, Job> specCache;

  public SpecCachingSchedulerJobClient(JobPersistence jobPersistence) {
    super(jobPersistence);
    specCache = CacheBuilder.newBuilder().build();
  }

  @Override
  public Job createGetSpecJob(String dockerImage) throws IOException {
    final Optional<Job> cachedJob = Optional.ofNullable(specCache.getIfPresent(dockerImage));
    if (cachedJob.isPresent()) {
      LOGGER.debug("cache hit: " + dockerImage);
      return cachedJob.get();
    } else {
      LOGGER.debug("cache miss: " + dockerImage);
      final Job job = super.createGetSpecJob(dockerImage);
      specCache.put(dockerImage, job);
      return job;
    }
  }

  @Override
  public void resetCache() {
    specCache.invalidateAll();
  }

}
