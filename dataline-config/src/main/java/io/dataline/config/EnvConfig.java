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

import java.nio.file.Path;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EnvConfig implements Configs {

  private static final Logger LOGGER = LoggerFactory.getLogger(EnvConfig.class);

  public static final String WORKSPACE_ROOT = "WORKSPACE_ROOT";
  public static final String CONFIG_ROOT = "CONFIG_ROOT";

  private final Function<String, String> getEnv;

  public EnvConfig() {
    this(System::getenv);
  }

  EnvConfig(final Function<String, String> getEnv) {
    this.getEnv = getEnv;
  }

  @Override
  public Path getWorkspaceRoot() {
    return getPath(WORKSPACE_ROOT);
  }

  @Override
  public Path getConfigRoot() {
    return getPath(CONFIG_ROOT);
  }

  private Path getPath(final String name) {
    final String value = getEnv.apply(name);
    if (value == null) {
      throw new IllegalArgumentException("Env variable not defined: " + name);
    }
    return Path.of(value);
  }
}
