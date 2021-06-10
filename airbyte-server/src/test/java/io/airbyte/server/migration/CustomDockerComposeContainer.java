package io.airbyte.server.migration;

import java.io.File;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import org.testcontainers.containers.DockerComposeContainer;
import org.testcontainers.containers.SocatContainer;

public class CustomDockerComposeContainer {

  private final DockerComposeContainer dockerComposeContainer;

  public CustomDockerComposeContainer(DockerComposeContainer dockerComposeContainer) {
    this.dockerComposeContainer = dockerComposeContainer;
  }

  public void start() {
    dockerComposeContainer.start();
  }

  public void stop()
      throws NoSuchFieldException, IllegalAccessException, NoSuchMethodException, InvocationTargetException {
    Class<? extends DockerComposeContainer> dockerComposeContainerClass = dockerComposeContainer
        .getClass();
    try {
      Field ambassadorContainerField = dockerComposeContainerClass.getDeclaredField("ambassadorContainer");
      ambassadorContainerField.setAccessible(true);
      SocatContainer ambassadorContainer = (SocatContainer) ambassadorContainerField
          .get(dockerComposeContainer);
      ambassadorContainer.stop();

      String cmd = "down ";

      Method runWithComposeMethod = dockerComposeContainerClass
          .getDeclaredMethod("runWithCompose", String.class);
      runWithComposeMethod.setAccessible(true);
      runWithComposeMethod.invoke(dockerComposeContainer, cmd);

    } finally {
      Field projectField = dockerComposeContainerClass.getDeclaredField("project");
      projectField.setAccessible(true);

      Method randomProjectId = dockerComposeContainerClass
          .getDeclaredMethod("randomProjectId");
      randomProjectId.setAccessible(true);
      String newProjectValue = (String) randomProjectId.invoke(dockerComposeContainer);

      projectField.set(dockerComposeContainer, newProjectValue);
    }
  }
}
