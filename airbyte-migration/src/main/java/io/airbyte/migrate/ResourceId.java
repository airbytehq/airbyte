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

package io.airbyte.migrate;

import com.google.common.base.Preconditions;
import java.nio.file.Path;
import java.util.Objects;

public class ResourceId {

  private final ResourceType type;
  private final String name;

  /**
   * Constructs a {@link ResourceId} from a {@link ResourceType} and a path. Assumes the file name is
   * snake case (case agnostic). The file name (without the yaml extension) is used as the name. If
   * the input file is not a yaml, this will break.
   *
   * @param resourceType type of the resource
   * @param path path that to be used to generate resource name
   * @return the resource id
   */
  public static ResourceId fromRecordFilePath(ResourceType resourceType, Path path) {
    // we can change this precondition in the future if our scheme changes, but for now fail loudly when
    // we get unexpected paths.
    Preconditions.checkState(path.getFileName().toString().endsWith(".yaml"), "ResourceId constructor expected yaml file.");

    return new ResourceId(
        resourceType,
        path.getFileName().toString().replace(".yaml", "").toUpperCase());
  }

  /**
   * Constructs a {@link ResourceId} from a {@link ResourceType} and a path. The file name (without
   * the yaml extension) is used as the name. If the input file is not a yaml, this will break.
   *
   * @param resourceType type of the resource
   * @param name name of the resource. Must be constant case. e.g. MY_CONSTANT.
   * @return the resource id
   */
  public static ResourceId fromConstantCase(ResourceType resourceType, String name) {
    return new ResourceId(resourceType, name);
  }

  /**
   * Create a ResourceId
   *
   * @param type type of the resource
   * @param name this string should be constant case e.g. MY_CONSTANT.
   */
  private ResourceId(ResourceType type, String name) {
    Preconditions.checkArgument(name.matches("^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$"), "name must be constant case. e.g MY_CONSTANT.");
    this.type = type;
    this.name = name;
  }

  public ResourceType getType() {
    return type;
  }

  public Path getResourceRelativePath() {
    return type.getDirectoryName().resolve(name + ".yaml");
  }

  public String getName() {
    return name;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ResourceId that = (ResourceId) o;
    return type == that.type && Objects.equals(name, that.name);
  }

  @Override
  public int hashCode() {
    return Objects.hash(type, name);
  }

  @Override
  public String toString() {
    return "ResourceId{" +
        "type=" + type +
        ", name='" + name + '\'' +
        '}';
  }

}
