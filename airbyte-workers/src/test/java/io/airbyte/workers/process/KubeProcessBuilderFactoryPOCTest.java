package io.airbyte.workers.process;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.util.Map;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.images.builder.ImageFromDockerfile;

public class KubeProcessBuilderFactoryPOCTest {
  private static final String ENTRYPOINT = "/tmp/run.sh";
  private static final String TEST_IMAGE_NAME = "np_dest:dev";

  @BeforeAll
  public static void setup() {
    // TODO(Davin): Why does building the container ahead doesn't work?
//    new GenericContainer(
//        new ImageFromDockerfile(TEST_IMAGE_NAME, false)
//            .withDockerfileFromBuilder(builder -> {
//                builder
//                    .from("debian")
//                    .env(Map.of("AIRBYTE_ENTRYPOINT", ENTRYPOINT))
//                    .entryPoint(ENTRYPOINT)
//                    .build();})).withEnv("AIRBYTE_ENTRYPOINT", ENTRYPOINT);
  }

  @Test
  @DisplayName("Should error if image does not have the right env var set.")
  public void testGetCommandFromImageNoCommand() {
    assertThrows(RuntimeException.class, () -> KubeProcessBuilderFactoryPOC.getCommandFromImage("hello-world"));
  }

  @Test
  @DisplayName("Should error if image does not exists.")
  public void testGetCommandFromImageBadImage() {
    assertThrows(RuntimeException.class, () -> KubeProcessBuilderFactoryPOC.getCommandFromImage("bad_missing_image"));
  }

  @Test
  @DisplayName("Should retrieve the right command if image has the right env var set.")
  public void testGetCommandFromImageCommandPresent() throws IOException {
    var command = KubeProcessBuilderFactoryPOC.getCommandFromImage(TEST_IMAGE_NAME);
    assertEquals(ENTRYPOINT, command);
  }

}
