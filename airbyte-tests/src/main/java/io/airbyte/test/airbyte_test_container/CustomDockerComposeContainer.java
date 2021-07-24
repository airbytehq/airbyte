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

package io.airbyte.test.airbyte_test_container;

import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import org.testcontainers.containers.DockerComposeContainer;
import org.testcontainers.containers.SocatContainer;

/**
 * we need this class to hack the method
 * {@link org.testcontainers.containers.DockerComposeContainer#stop()} so that we can do a docker
 * compose down without removing the volumes
 */
public class CustomDockerComposeContainer {

  private final DockerComposeContainer dockerComposeContainer;

  public CustomDockerComposeContainer(DockerComposeContainer dockerComposeContainer) {
    this.dockerComposeContainer = dockerComposeContainer;
  }

  public void start() {
    dockerComposeContainer.start();
  }

  /**
   * This method is hacked from {@link org.testcontainers.containers.DockerComposeContainer#stop()} We
   * needed to do this to avoid removing the volumes when the container is stopped so that the data
   * persists and can be tested against in the second run
   */
  @SuppressWarnings("rawtypes")
  public void stopRetainVolumes() throws NoSuchFieldException, IllegalAccessException, NoSuchMethodException, InvocationTargetException {
    final Class<? extends DockerComposeContainer> dockerComposeContainerClass = dockerComposeContainer.getClass();
    try {
      final Field ambassadorContainerField = dockerComposeContainerClass.getDeclaredField("ambassadorContainer");
      ambassadorContainerField.setAccessible(true);
      final SocatContainer ambassadorContainer = (SocatContainer) ambassadorContainerField.get(dockerComposeContainer);
      ambassadorContainer.stop();

      final String cmd = "down ";

      final Method runWithComposeMethod = dockerComposeContainerClass.getDeclaredMethod("runWithCompose", String.class);
      runWithComposeMethod.setAccessible(true);
      runWithComposeMethod.invoke(dockerComposeContainer, cmd);

    } finally {
      final Field projectField = dockerComposeContainerClass.getDeclaredField("project");
      projectField.setAccessible(true);

      final Method randomProjectId = dockerComposeContainerClass.getDeclaredMethod("randomProjectId");
      randomProjectId.setAccessible(true);
      final String newProjectValue = (String) randomProjectId.invoke(dockerComposeContainer);

      projectField.set(dockerComposeContainer, newProjectValue);
    }
  }

  public void stop() {
    dockerComposeContainer.stop();
  }

}
