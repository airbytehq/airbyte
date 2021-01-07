package io.airbyte.migrate;

import com.google.common.base.Preconditions;
import java.nio.file.Path;
import java.util.Objects;

public class ResourceId {

  private final ResourceType type;
  private final String name;

  /**
   * Constructs a {@link ResourceId} from a {@link ResourceType} and a path. The file name (without the yaml extension) is used as the name. If the input file is not a yaml, this will break.
   * @param resourceType type of the resource
   * @param path path that to be used to generate resource name
   * @return the resource id
   */
  public static ResourceId fromPath(ResourceType resourceType, Path path) {
    // we can change this precondition in the future if our scheme changes, but for now fail loudly when we get unexpected paths.
    Preconditions.checkState(path.getFileName().toString().endsWith(".yaml"), "ResourceId constructor expected yaml file.");

    return new ResourceId(
        resourceType,
        path.getFileName().toString().replace(".yaml", "")
    );
  }

  private ResourceId(ResourceType type, String name) {
    this.type = type;
    this.name = name;
  }

  public ResourceType getType() {
    return type;
  }

  public String getName() {
    return name;
  }

  public Path getResourceRelativePath() {
    return Path.of(type.toString().toLowerCase()).resolve(name + ".yaml");
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
