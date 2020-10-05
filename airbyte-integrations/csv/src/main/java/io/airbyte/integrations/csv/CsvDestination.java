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

package io.airbyte.integrations.csv;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.io.Resources;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnectionSpecification;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardDiscoverSchemaOutput;
import io.airbyte.config.Stream;
import io.airbyte.integrations.javabase.Destination;
import io.airbyte.integrations.javabase.DestinationConsumer;
import io.airbyte.integrations.javabase.JavaBaseConstants;
import io.airbyte.singer.SingerMessage;
import java.io.FileWriter;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CsvDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(CsvDestination.class);

  private static final String DESTINATION_PATH_FIELD = "destination_path";

  // todo (cgardens) - hack to handle the fact that the resources of this jar aren't in original
  // classpath. should try to find a way to handle this
  // outside of the runtime.
  private URLClassLoader getClassLoader() {
    final String destinationJarPath = System.getenv().get(JavaBaseConstants.ENV_DESTINATION_JAR_PATH);

    try {
      return new URLClassLoader(new URL[] {Path.of(destinationJarPath).toUri().toURL()});
    } catch (MalformedURLException e) {
      throw new RuntimeException(e);
    }
  }

  @SuppressWarnings("UnstableApiUsage")
  @Override
  public DestinationConnectionSpecification spec() throws IOException {
    final String resourceString = Resources.toString(getClassLoader().findResource("spec.json"), StandardCharsets.UTF_8);
    return Jsons.deserialize(resourceString, DestinationConnectionSpecification.class);
  }

  @Override
  public StandardCheckConnectionOutput check(JsonNode config) {
    try {
      FileUtils.forceMkdir(getDestinationPath(config).toFile());
    } catch (IOException e) {
      return new StandardCheckConnectionOutput().withStatus(Status.FAILURE).withMessage(e.getMessage());
    }
    return new StandardCheckConnectionOutput().withStatus(Status.SUCCESS);
  }

  @Override
  public StandardDiscoverSchemaOutput discover(JsonNode config) {
    throw new RuntimeException("Not Implemented");
  }

  @Override
  public DestinationConsumer<SingerMessage> write(JsonNode config, Schema schema) throws IOException {
    final Path destinationDir = getDestinationPath(config);

    FileUtils.forceMkdir(destinationDir.toFile());

    final long now = Instant.now().toEpochMilli();
    final Map<String, WriteConfig> map = new HashMap<>();
    for (final Stream stream : schema.getStreams()) {
      Path tmpPath = destinationDir.resolve(stream.getName() + "_" + now + ".csv");
      Path finalPath = destinationDir.resolve(stream.getName() + ".csv");
      final FileWriter fileWriter = new FileWriter(tmpPath.toFile());
      map.put(stream.getName(), new WriteConfig(fileWriter, tmpPath, finalPath));
    }

    return new CsvConsumer(map);
  }

  /**
   * Extract provided relative path from csv config object and append to local mount path.
   *
   * @param config - csv config object
   * @return absolute path with the relative path appended to the local volume mount.
   */
  private Path getDestinationPath(JsonNode config) {
    final String destinationRelativePath = config.get(DESTINATION_PATH_FIELD).asText();
    Preconditions.checkNotNull(destinationRelativePath);

    // append destination path to the local mount.
    return JavaBaseConstants.LOCAL_MOUNT.resolve(destinationRelativePath);
  }

  public static class WriteConfig {

    private final FileWriter fileWriter;
    private final Path tmpPath;
    private final Path finalPath;

    public WriteConfig(FileWriter fileWriter, Path tmpPath, Path finalPath) {
      this.fileWriter = fileWriter;
      this.tmpPath = tmpPath;
      this.finalPath = finalPath;
    }

    public FileWriter getFileWriter() {
      return fileWriter;
    }

    public Path getTmpPath() {
      return tmpPath;
    }

    public Path getFinalPath() {
      return finalPath;
    }

  }

  public static class CsvConsumer implements DestinationConsumer<SingerMessage> {

    private final Map<String, WriteConfig> writeConfigs;

    public CsvConsumer(Map<String, WriteConfig> writeConfigs) {
      this.writeConfigs = writeConfigs;
    }

    @Override
    public void accept(SingerMessage singerMessage) throws IOException {
      if (writeConfigs.containsKey(singerMessage.getStream())) {
        // todo (cgardens) - this isn't actually storing csv yet, just json. focus of this PR is how you
        // would use the javabase. will not merge this
        // as part of the PR.
        writeConfigs.get(singerMessage.getStream()).getFileWriter().write(Jsons.serialize(singerMessage.getValue()));
      }
    }

    @Override
    public void complete() throws IOException {
      LOGGER.info("finalizing consumer.");
      for (final WriteConfig writeConfig : writeConfigs.values()) {
        Files.move(writeConfig.getTmpPath(), writeConfig.getFinalPath(), StandardCopyOption.REPLACE_EXISTING);
      }
    }

    @Override
    public void close() {
      LOGGER.info("closing consumer.");
      // no op. no connection to close.
    }

  }

}
