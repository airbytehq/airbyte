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

package io.airbyte.integrations.base;

import com.google.common.base.Preconditions;

public class IntegrationConfig {

  private final Command command;
  private final String config;
  private final String schema;
  private final String state;

  private IntegrationConfig(Command command, String config, String schema, String state) {
    this.command = command;
    this.config = config;
    this.schema = schema;
    this.state = state;
  }

  public static IntegrationConfig spec() {
    return new IntegrationConfig(Command.SPEC, null, null, null);
  }

  public static IntegrationConfig check(String config) {
    Preconditions.checkNotNull(config);
    return new IntegrationConfig(Command.CHECK, config, null, null);
  }

  public static IntegrationConfig discover(String config) {
    Preconditions.checkNotNull(config);
    return new IntegrationConfig(Command.DISCOVER, config, null, null);
  }

  public static IntegrationConfig read(String config, String schema, String state) {
    Preconditions.checkNotNull(config);
    Preconditions.checkNotNull(schema);
    return new IntegrationConfig(Command.READ, config, schema, state);
  }

  public static IntegrationConfig write(String config, String schema) {
    Preconditions.checkNotNull(config);
    Preconditions.checkNotNull(schema);
    return new IntegrationConfig(Command.WRITE, config, schema, null);
  }

  public Command getCommand() {
    return command;
  }

  public String getConfig() {
    Preconditions.checkState(command != Command.SPEC);
    return config;
  }

  public String getSchema() {
    Preconditions.checkState(command == Command.READ || command == Command.WRITE);
    return schema;
  }

  public String getState() {
    Preconditions.checkState(command == Command.READ);
    return state;
  }

  @Override
  public String toString() {
    return "IntegrationConfig{" +
        "command=" + command +
        ", config='" + config + '\'' +
        ", schema='" + schema + '\'' +
        ", state='" + state + '\'' +
        '}';
  }
}
