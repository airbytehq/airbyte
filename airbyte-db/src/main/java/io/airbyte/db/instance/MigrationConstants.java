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

package io.airbyte.db.instance;

public class MigrationConstants {

  public static final String BASELINE_VERSION = "0.29.0.001";
  public static final String BASELINE_DESCRIPTION = "Baseline from file-based migration v1";
  public static final boolean BASELINE_ON_MIGRATION = true;

  public static final String CONFIGS_DB_MIGRATION_LOCATION = "classpath:io/airbyte/db/instance/configs/migrations";
  public static final String JOBS_DB_MIGRATION_LOCATION = "classpath:io/airbyte/db/instance/jobs/migrations";

  public static final String CONFIGS_DB_SCHEMA_DUMP = "src/main/resources/configs_database/schema_dump.txt";
  public static final String JOBS_DB_SCHEMA_DUMP = "src/main/resources/jobs_database/schema_dump.txt";

}
