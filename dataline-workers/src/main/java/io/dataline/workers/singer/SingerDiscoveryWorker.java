/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.workers.singer;

import static io.dataline.workers.JobStatus.FAILED;
import static io.dataline.workers.JobStatus.SUCCESSFUL;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.PropertiesProperty;
import io.dataline.config.Schema;
import io.dataline.config.SingerCatalog;
import io.dataline.config.SingerType;
import io.dataline.config.StandardDiscoveryOutput;
import io.dataline.config.Table;
import io.dataline.workers.DiscoverSchemaWorker;
import io.dataline.workers.OutputAndStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static io.dataline.workers.JobStatus.FAILED;
import static io.dataline.workers.JobStatus.SUCCESSFUL;


public class SingerDiscoveryWorker extends BaseSingerWorker<StandardDiscoveryOutput>
    implements DiscoverSchemaWorker {
  // TODO log errors to specified file locations
  private static Logger LOGGER = LoggerFactory.getLogger(SingerDiscoveryWorker.class);
  private static String CONFIG_JSON_FILENAME = "config.json";
  private static String CATALOG_JSON_FILENAME = "catalog.json";
  private static String ERROR_LOG_FILENAME = "err.log";

  private final String configDotJson;
  private final SingerTap tap;
  private volatile Process workerProcess;

  public SingerDiscoveryWorker(
      String workerId,
      String configDotJson,
      SingerTap tap,
      String workspaceRoot,
      String singerLibsRoot) {
    super(workerId, workspaceRoot, singerLibsRoot);
    this.configDotJson = configDotJson;
    this.tap = tap;
  }

  @Override
  OutputAndStatus<StandardDiscoveryOutput> runInternal() {
    // TODO use format converter here
    // write config.json to disk
    String configPath = writeFileToWorkspace(CONFIG_JSON_FILENAME, configDotJson);

    String tapPath = getExecutableAbsolutePath(tap);

    String catalogDotJsonPath =
        getWorkspacePath().resolve(CATALOG_JSON_FILENAME).toAbsolutePath().toString();
    String errorLogPath =
        getWorkspacePath().resolve(ERROR_LOG_FILENAME).toAbsolutePath().toString();

    // exec
    try {
      String[] cmd = {tapPath, "--config", configPath, "--discover"};

      workerProcess =
          new ProcessBuilder(cmd)
              .redirectError(new File(errorLogPath))
              .redirectOutput(new File(catalogDotJsonPath))
              .start();

      while (!workerProcess.waitFor(1, TimeUnit.MINUTES)) {
        LOGGER.info("Waiting for discovery worker {}", workerId);
      }

      int exitCode = workerProcess.exitValue();
      if (exitCode == 0) {
        String catalog = readFileFromWorkspace(CATALOG_JSON_FILENAME);
        final SingerCatalog singerCatalog = jsonCatalogToTyped(catalog);
        final StandardDiscoveryOutput discoveryOutput = toDiscoveryOutput(singerCatalog);
        return new OutputAndStatus<>(SUCCESSFUL, discoveryOutput);
      } else {
        String errLog = readFileFromWorkspace(ERROR_LOG_FILENAME);
        LOGGER.debug(
            "Discovery worker {} subprocess finished with exit code {}. Error log: {}",
            workerId,
            exitCode,
            errLog);
        return new OutputAndStatus<>(FAILED);
      }
    } catch (IOException | InterruptedException e) {
      LOGGER.error("Exception running discovery: ", e);
      throw new RuntimeException(e);
    }
  }

  private static SingerCatalog jsonCatalogToTyped(String catalogJson) {
    final ObjectMapper objectMapper = new ObjectMapper();

    try {
      return objectMapper.readValue(catalogJson, SingerCatalog.class);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private static StandardDiscoveryOutput toDiscoveryOutput(SingerCatalog catalog) {
    List<Table> tableStream =
        catalog.getStreams().stream()
            .map(
                stream -> {
                  final Table table = new Table();
                  table.setName(stream.getStream()); // ?
                  table.setColumns(
                      stream
                          .getSchema()
                          .getProperties()
                          .getAdditionalProperties()
                          .entrySet()
                          .stream()
                          .map(
                              entry -> {
                                final String columnName = entry.getKey();
                                final PropertiesProperty columnMetadata = entry.getValue();
                                final Column column = new Column();
                                column.setName(columnName);
                                column.setDataType(singerTypesToDataType(columnMetadata.getType()));
                                return column;
                              })
                          .collect(Collectors.toList()));
                  return table;
                })
            .collect(Collectors.toList());

    final Schema schema = new Schema();
    schema.setTables(tableStream);
    final StandardDiscoveryOutput discoveryOutput = new StandardDiscoveryOutput();
    discoveryOutput.setSchema(schema);

    return discoveryOutput;
  }

  /**
   * Singer tends to have 2 types for columns one of which is null. The null is pretty irrelevant,
   * so look at types and find the first non-null one and use that.
   *
   * @param singerTypes - list of types discovered by singer.
   * @return reduce down to one type which best matches the column's data type
   */
  private static DataType singerTypesToDataType(List<SingerType> singerTypes) {
    return singerTypes.stream()
        .filter(singerType -> !SingerType.NULL.equals(singerType))
        .map(SingerDiscoveryWorker::singerTypeToDataType)
        .findFirst()
        .orElse(DataType.STRING);
  }

  /**
   * Singer doesn't seem to have an official list of the data types that they support, so we will
   * have to do our best here as we discover them. If it becomes too awful, we can just map types we
   * don't recognize to string.
   *
   * @param singerType - singer's column data type
   * @return best match for our own data type
   */
  private static DataType singerTypeToDataType(SingerType singerType) {
    switch (singerType) {
      case STRING:
        return DataType.STRING;
      case INTEGER:
        return DataType.NUMBER;
      case NULL:
        //noinspection DuplicateBranchesInSwitch
        return DataType.STRING; // todo (cgardens) - hackasaurus rex
      case BOOLEAN:
        return DataType.BOOLEAN;
      default:
        throw new RuntimeException(
            String.format("could not map SingerType: %s to DataType", singerType));
    }
  }

  @Override
  public void cancel() {
    cancelHelper(workerProcess);
  }
}
