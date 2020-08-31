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

package io.dataline.config;

public enum ConfigSchema {

  // workspace
  STANDARD_WORKSPACE("StandardWorkspace.json"),

  // source
  STANDARD_SOURCE("StandardSource.json"),
  SOURCE_CONNECTION_SPECIFICATION("SourceConnectionSpecification.json"),
  SOURCE_CONNECTION_IMPLEMENTATION("SourceConnectionImplementation.json"),

  // destination
  STANDARD_DESTINATION("StandardDestination.json"),
  DESTINATION_CONNECTION_SPECIFICATION("DestinationConnectionSpecification.json"),
  DESTINATION_CONNECTION_IMPLEMENTATION("DestinationConnectionImplementation.json"),

  // test connection
  STANDARD_CONNECTION_STATUS("StandardConnectionStatus.json"),

  // discover schema
  STANDARD_DISCOVERY_OUTPUT("StandardDiscoveryOutput.json"),

  // sync
  STANDARD_SYNC("StandardSync.json"),
  STANDARD_SYNC_SUMMARY("StandardSyncSummary.json"),
  STANDARD_SYNC_SCHEDULE("StandardSyncSchedule.json"),
  STATE("State.json");

  private final String schemaFilename;

  ConfigSchema(String schemaFilename) {
    this.schemaFilename = schemaFilename;
  }

  public String getSchemaFilename() {
    return schemaFilename;
  }

  public static String getSchemaDirectory() {
    return "json/";
  }

}
