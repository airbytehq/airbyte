package io.dataline.conduit.workers.singer;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

public class SingerUtils {
  private static String WORKSPACE_PATH = "workspace/singer/";
  private static String SINGER_LIBS_PATH = "lib/singer";

  public static void testTapConnection(SingerTap tap, String tapConfiguration) {}

  public static DiscoveryOutput discoverTap(SingerTap tap, String configJson) {
    // TODO opid should probably be input so it can match scheduler IDs
    String operationId = UUID.randomUUID().toString();
    Path workspacePath = getWorkspacePath(operationId);
    // write config.json to disk
    workspacePath.resolve()
    writeJsonToWorkspace(configPath, configJson);

    // get path for tap binary
    String tapPath = tap.getExecutablePath();

    // exec
    try {
      Runtime.getRuntime().exec(new String[] {
              tapPath,
              "--config " +

      });
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    // read catalog.json and return as string
  }

  private static Path getWorkspacePath(String operationId) {
    return Paths.get(WORKSPACE_PATH, operationId);
  }

  public static SyncOutput runSync(
      SingerTap tap,
      String tapConfiguration,
      String tapCatalog,
      String state,
      SingerTarget target,
      String targetConfig) {

    return null;
  }

  private static String readFile(Path path) {};

  private static void writeJsonToWorkspace(Path path, String jsonContents) {
    try {
      FileWriter fileWriter = new FileWriter(path.toFile());
      fileWriter.write(jsonContents);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private static String getSingerTapPath(SingerTap tap) {}

  public static class TestTapError {}

  public static class TestTapOutput {}

  public static class DiscoveryError {}

  public static class DiscoveryOutput {
    public final String catalog;

    public DiscoveryOutput(String catalog) {
      this.catalog = catalog;
    }
  }

  public static class SyncError {}

  public static class SyncOutput {
    public final String state;

    public SynchronizeOutput(String state) {
      this.state = state;
    }
  }
}
