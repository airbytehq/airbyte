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

/**
 * This class is the entrypoint Class to initiate export, import or transformation operations and manipulate
 * the various data entities in Airbyte.
 */
public class AirbyteMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteMigration.class);

  public static void main(String[] args) throws Exception {
    LOGGER.info("starting migration: {}", AirbyteMigration.class);
    AirbyteMigration migration = new AirbyteMigration();
    // TODO: Parse from args instead
    final String previousConfigs = "/tmp/old_airbyte_config.yaml";
    final String newConfigs = "/tmp/new_airbyte_config.yaml";
    final String previousJobs = "/tmp/old_airbyte_jobs.yaml";
    final String newJobs = "/tmp/new_airbyte_jobs.yaml";
    // TODO: Run export / import or transform operations depending on args instead
    migration.testMigrateConfigs(previousConfigs, newConfigs);
    migration.testMigrateJobs(previousJobs, newJobs);
    LOGGER.info("completed migration: {}", AirbyteMigration.class);
  }

  private void testMigrateConfigs(String previousConfigs, String newConfigs) {
    final AirbyteConfigIO configs = new AirbyteConfigIO();
    final AirbyteConfigMigration configMigration = new AirbyteConfigMigration();
    configs.exportData(previousConfigs);
    configMigration.transformData(previousConfigs, newConfigs);
    configs.importData(newConfigs);
  }

  private void testMigrateJobs(String previousJobs, String newJobs) {
    final AirbyteJobsIO jobs = new AirbyteJobsIO();
    final AirbyteJobsMigration jobsMigration = new AirbyteJobsMigration();
    jobs.exportData(previousJobs);
    jobsMigration.transformData(previousJobs, newJobs);
    jobs.importData(newJobs);
  }

}
