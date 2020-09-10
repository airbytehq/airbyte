package io.dataline.integrations.io.dataline.integration_tests.sources;

import io.dataline.config.StandardTapConfig;
import io.dataline.db.PostgreSQLContainerHelper;
import io.dataline.workers.process.DockerProcessBuilderFactory;
import io.dataline.workers.process.ProcessBuilderFactory;
import io.dataline.workers.singer.SingerDiscoverSchemaWorker;
import io.dataline.workers.singer.SingerTapFactory;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class SingerPostgresSourceTest {

  private static final String IMAGE_NAME = "dataline/integration-singer-postgres-source";
  private static final Path TESTS_PATH = Path.of("/tmp/dataline_integration_tests");

  private PostgreSQLContainer psqlDb;
  private ProcessBuilderFactory pbf;
  private Path workspaceRoot;
  private Path jobRoot;

  @BeforeEach
  public void init() throws IOException {
    psqlDb = new PostgreSQLContainer();
    psqlDb.start();

    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("simple_postgres_init.sql"), psqlDb);
    Files.createDirectories(TESTS_PATH);
    workspaceRoot = Files.createTempDirectory(TESTS_PATH, "dataline-integration");
    jobRoot = workspaceRoot.resolve("job");
    Files.createDirectories(jobRoot);

    pbf = new DockerProcessBuilderFactory(workspaceRoot, jobRoot.toString(), "host");
  }

  @AfterEach
  public void cleanUp() {
    psqlDb.stop();
  }

  @Test
  public void testRead() {
    SingerTapFactory singerTapFactory = new SingerTapFactory(IMAGE_NAME, pbf, new SingerDiscoverSchemaWorker(IMAGE_NAME, pbf));

    StandardTapConfig tapConfig = new StandardTapConfig().with
    singerTapFactory.create()
  }

  @Test
  public void testDiscover() {

  }

  @Test
  public void testSuccessfulConnectionCheck() {

  }

  @Test
  public void testInvalidCredsFailedConnectionCheck() {

  }
}
