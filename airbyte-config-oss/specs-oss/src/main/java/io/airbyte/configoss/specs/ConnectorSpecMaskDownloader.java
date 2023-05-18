/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.configoss.specs;

import io.airbyte.commons.cli.Clis;
import java.net.URL;
import java.nio.file.Path;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConnectorSpecMaskDownloader {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConnectorSpecMaskDownloader.class);

  private static final String REMOTE_SPEC_SECRET_MASK_URL =
      "https://connectors.airbyte.com/files/registries/v0/specs_secrets_mask.yaml";
  public static final String MASK_FILE = "specs_secrets_mask.yaml";
  private static final Option SPEC_ROOT_OPTION = Option.builder("s").longOpt("specs-root").hasArg(true).required(true)
      .desc("path to where spec files are stored").build();
  private static final Options OPTIONS = new Options().addOption(SPEC_ROOT_OPTION);

  /**
   * This method is to download the Spec Mask File from the remote URL and save it to the local
   * resource folder.
   */
  public static void main(final String[] args) throws Exception {
    final CommandLine parsed = Clis.parse(args, OPTIONS);
    final Path specRoot = Path.of(parsed.getOptionValue(SPEC_ROOT_OPTION.getOpt()));
    final Path writePath = specRoot.resolve(MASK_FILE);
    LOGGER.info("Downloading Spec Secret Mask from {} to {}", REMOTE_SPEC_SECRET_MASK_URL, writePath);

    final int timeout = 10000;
    FileUtils.copyURLToFile(new URL(REMOTE_SPEC_SECRET_MASK_URL), writePath.toFile(), timeout, timeout);
  }

}
