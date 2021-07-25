package io.airbyte.config.helpers;

import io.airbyte.commons.string.Strings;
import io.airbyte.config.EnvConfigs;
import java.io.IOException;
import java.nio.file.Path;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Tag("log4j2-config")
public class KubeLoggingConfigTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(KubeLoggingConfigTest.class);
  private static final String RUN_TEST_ENV_VAR = "TEST_LOGGER";
  // We publish every minute. See log4j2.xml.
  private static final long LOG_PUBLISH_DELAY = 60 * 1000;

  /**
   * Because this test tests our env var set up is compatible with our Log4j2 configuration, we are unable to perform injection, and
   * instead rely on env vars set in ./tools/bin/cloud_storage_logging_test.sh.
   *
   * This test will fail if certain env vars aren't set, so only run if {@link #RUN_TEST_ENV_VAR} is defined.
   */
  @Test
  public void testLoggingConfiguration() throws IOException, InterruptedException {
    System.out.println("======= log4j2-config tests");
//    if (System.getenv(RUN_TEST_ENV_VAR) != null) {
//      var randPath = Path.of(Strings.addRandomSuffix("","", 5));
//      // This mirror our Log4j2 set up. See log4j2.xml.
//      LogClientSingleton.setJobMdc(randPath);
//
//      LOGGER.info("line 1");
//      LOGGER.info("line 2");
//      LOGGER.info("line 3");
//
//      // Sleep to make sure the logs appear.
//      Thread.sleep(LOG_PUBLISH_DELAY);
//
//      // The same env vars that log4j2 uses to determine where to publish to
//      var a = LogClientSingleton.getJobLogFile(new EnvConfigs(), randPath);
//      System.out.println(a);
//    }
  }

}
