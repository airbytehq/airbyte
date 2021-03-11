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

package io.airbyte.server.handlers;

import io.airbyte.api.model.HealthCheckRead;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HealthCheckHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(HealthCheckHandler.class);

  private final ConfigRepository configRepository;

  public HealthCheckHandler(ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  // todo (cgardens) - add more checks as we go.
  public HealthCheckRead health() {
    boolean databaseHealth = false;
    try {
      databaseHealth = configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID, true) != null;
    } catch (Exception e) {
      LOGGER.error("database health check failed.");
    }

    return new HealthCheckRead().db(databaseHealth);
  }

}
