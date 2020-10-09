package io.airbyte.commons.docker;

public class DockerUtil {
  public static String getTaggedImageName(String dockerRepository, String tag){
    return String.join(":", dockerRepository, tag);
  }
}
