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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.Schema;
import io.dataline.config.SingerCatalog;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.workers.DiscoverSchemaWorker;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerDiscoverSchemaWorker
    extends BaseSingerWorker<StandardDiscoverSchemaInput, StandardDiscoverSchemaOutput>
    implements DiscoverSchemaWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerDiscoverSchemaWorker.class);

  // TODO log errors to specified file locations
  private static String CONFIG_JSON_FILENAME = "config.json";
  private static String CATALOG_JSON_FILENAME = "catalog.json";
  private static String ERROR_LOG_FILENAME = "err.log";

  private volatile Process workerProcess;
  private final String imageName;

  public SingerDiscoverSchemaWorker(String imageName) {
    this.imageName = imageName;
  }

  // package private since package-local classes need direct access to singer catalog, and the
  // conversion from SingerSchema to Dataline schema is lossy
  OutputAndStatus<SingerCatalog> runInternal(
      StandardDiscoverSchemaInput discoverSchemaInput, Path workspaceRoot)
      throws InvalidCredentialsException {
    // todo (cgardens) - just getting original impl to line up with new iface for now. this can be
    //   reduced.
    final ObjectMapper objectMapper = new ObjectMapper();
    final String configDotJson;
    try {
      configDotJson =
          objectMapper.writeValueAsString(discoverSchemaInput.getConnectionConfiguration());
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }

    writeFile(workspaceRoot, CONFIG_JSON_FILENAME, configDotJson);

    // exec
    try {
      final String[] cmd = {
        "docker",
        "run",
        "-v",
        "gradlew-tmp:/tmp",
        "-w",
        workspaceRoot.toString(),
        "--entrypoint",
        "/bin/sh",
        "--network=host",
        imageName,
        //        "--config",
        //        CONFIG_JSON_FILENAME,
        //        "--discover"
        "-c",
        "sleep 999999"
      };

      System.out.println("Arrays.toString(cmd) = " + Arrays.toString(cmd));

      workerProcess =
          new ProcessBuilder(cmd)
              .redirectError(getFullPath(workspaceRoot, ERROR_LOG_FILENAME).toFile())
              .redirectOutput(getFullPath(workspaceRoot, CATALOG_JSON_FILENAME).toFile())
              .start();

      while (!workerProcess.waitFor(1, TimeUnit.MINUTES)) {
        LOGGER.info("Waiting for discovery job.");
      }

      int exitCode = workerProcess.exitValue();
      if (exitCode == 0) {
        String catalog = readFile(workspaceRoot, CATALOG_JSON_FILENAME);
        final SingerCatalog singerCatalog = jsonCatalogToTyped(catalog);
        return new OutputAndStatus<>(SUCCESSFUL, singerCatalog);
      } else {
        // TODO throw invalid credentials exception where appropriate based on error log
        String errLog = readFile(workspaceRoot, ERROR_LOG_FILENAME);
        LOGGER.debug(
            "Discovery job subprocess finished with exit code {}. Error log: {}", exitCode, errLog);
        return new OutputAndStatus<>(FAILED);
      }
    } catch (IOException | InterruptedException e) {
      LOGGER.error("Exception running discovery: ", e);
      throw new RuntimeException(e);
    }
  }

  @Override
  public OutputAndStatus<StandardDiscoverSchemaOutput> run(
      StandardDiscoverSchemaInput discoverSchemaInput, Path workspaceRoot)
      throws InvalidCredentialsException {
    OutputAndStatus<SingerCatalog> output = runInternal(discoverSchemaInput, workspaceRoot);
    JobStatus status = output.getStatus();

    OutputAndStatus<StandardDiscoverSchemaOutput> finalOutput;
    if (output.getOutput().isPresent()) {
      return new OutputAndStatus<>(status, toDiscoveryOutput(output.getOutput().get()));
    } else {
      return new OutputAndStatus<>(status);
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

  private static StandardDiscoverSchemaOutput toDiscoveryOutput(SingerCatalog catalog) {
    final Schema schema = SingerCatalogConverters.toDatalineSchema(catalog);
    final StandardDiscoverSchemaOutput output = new StandardDiscoverSchemaOutput();
    output.setSchema(schema);

    return output;
  }

  @Override
  public void cancel() {
    cancelHelper(workerProcess);
  }
}
