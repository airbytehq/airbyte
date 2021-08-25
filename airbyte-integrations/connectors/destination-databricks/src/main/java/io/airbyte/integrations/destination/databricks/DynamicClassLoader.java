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

package io.airbyte.integrations.destination.databricks;

import java.io.IOException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Paths;

public final class DynamicClassLoader extends URLClassLoader {

  static {
    registerAsParallelCapable();
  }

  public DynamicClassLoader(String name, ClassLoader parent) {
    super(name, new URL[0], parent);
  }

  /*
   * Required when this classloader is used as the system classloader
   */
  public DynamicClassLoader(ClassLoader parent) {
    this("classpath", parent);
  }

  public DynamicClassLoader() {
    this(Thread.currentThread().getContextClassLoader());
  }

  void add(URL url) {
    addURL(url);
  }

  public static DynamicClassLoader findAncestor(ClassLoader cl) {
    do {

      if (cl instanceof DynamicClassLoader)
        return (DynamicClassLoader) cl;

      cl = cl.getParent();
    } while (cl != null);

    return null;
  }

  /*
   *  Required for Java Agents when this classloader is used as the system classloader
   */
  @SuppressWarnings("unused")
  private void appendToClassPathForInstrumentation(String jarfile) throws IOException {
    add(Paths.get(jarfile).toRealPath().toUri().toURL());
  }
}
