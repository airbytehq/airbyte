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

package io.airbyte.server.validators;

import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.handlers.SchedulerHandler;

public class DockerImageValidator {

  private final SchedulerHandler schedulerHandler;

  public DockerImageValidator(SchedulerHandler schedulerHandler) {
    this.schedulerHandler = schedulerHandler;
  }

  /**
   * @throws KnownException if it is unable to verify that the input image is a valid connector
   *         definition image.
   */
  public void assertValidIntegrationImage(String dockerRepository, String imageTag) throws KnownException {
    // Validates that the docker image exists and can generate a compatible spec by running a getSpec
    // job on the provided image.
    String imageName = DockerUtils.getTaggedImageName(dockerRepository, imageTag);
    try {
      schedulerHandler.getConnectorSpecification(imageName);
    } catch (Exception e) {
      throw new KnownException(422, "Encountered an issue while validating input docker image: " + e.getMessage());
    }
  }

}
