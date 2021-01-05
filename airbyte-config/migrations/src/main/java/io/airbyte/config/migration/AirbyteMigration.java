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

package io.airbyte.config.migration;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteMigration.class);

  public static void main(String[] args) throws Exception {
    LOGGER.info("starting migration: {}", AirbyteMigration.class);
    AirbyteMigration migration = new AirbyteMigration();
    // TODO: Parse from args instead
    final String previousConfigs = "/tmp/airbyte_config.yaml";
    final String previousJobs = "/tmp/airbyte_jobs.yaml";
    migration.migrateConfigs(previousConfigs);
    migration.migrateJobs(previousJobs);
    LOGGER.info("completed migration: {}", AirbyteMigration.class);
  }

  private void migrateConfigs(String previousConfigs) {
    final AirbyteConfigIO configs = new AirbyteConfigIO();
    final AirbyteConfigMigration configMigration = new AirbyteConfigMigration();
    configs.exportData(previousConfigs);
    final String newConfigs = configMigration.transformData(previousConfigs);
    configs.importData(newConfigs);
  }

  private void migrateJobs(String previousJobs) {
    final AirbyteJobsIO jobs = new AirbyteJobsIO();
    final AirbyteJobsMigration jobsMigration = new AirbyteJobsMigration();
    jobs.exportData(previousJobs);
    final String newJobs = jobsMigration.transformData(previousJobs);
    jobs.importData(newJobs);
  }

}
