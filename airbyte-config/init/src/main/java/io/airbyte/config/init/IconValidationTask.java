/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import com.google.common.io.Resources;
import io.airbyte.config.CatalogDefinitionsConfig;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Simple task that checks if all icons in the seed definition files exist as well as
 * that no icon in the icons folder is unused.
 */
public class IconValidationTask {

  private static String ICON_SUB_DIRECTORY = CatalogDefinitionsConfig.getIconSubdirectory();

  private static Path getIconDirectoryPath() {
    try {
      final URI localIconsUri = Resources.getResource(ICON_SUB_DIRECTORY).toURI();
      return Path.of(localIconsUri);
    } catch (final URISyntaxException e) {
      throw new RuntimeException("Failed to fetch local icon directory path", e);
    }
  }

  private static List<String> getLocalIconFileNames() {
    try {
      final Path iconDirectoryPath = getIconDirectoryPath();
      return Files.list(iconDirectoryPath).map(path -> path.getFileName().toString()).toList();
    } catch (final IOException e) {
      throw new RuntimeException("Failed to fetch local icon files", e);
    }
  }

  private static List<String> getIconFileNamesFromCatalog() {
    final LocalDefinitionsProvider localDefinitionsProvider = new LocalDefinitionsProvider();
    final List<String> sourceIcons = localDefinitionsProvider
        .getSourceDefinitions()
        .stream().map(s -> s.getIcon())
        .collect(Collectors.toList());

    final List<String> destinationIcons = localDefinitionsProvider
        .getDestinationDefinitions()
        .stream().map(s -> s.getIcon())
        .collect(Collectors.toList());

    // concat the two lists one
    sourceIcons.addAll(destinationIcons);
    return sourceIcons;
  }

  public static void main(final String[] args) throws Exception {
    final List<String> catalogIconFileNames = getIconFileNamesFromCatalog();
    final List<String> localIconFileNames = getLocalIconFileNames();

    // Get all icons that are in the catalog but not in the local icons folder
    final List<String> missingIcons = catalogIconFileNames.stream()
        .filter(icon -> !localIconFileNames.contains(icon))
        .toList();

    // Get all icons that are in the local icons folder but not in the catalog
    final List<String> unusedIcons = localIconFileNames.stream()
        .filter(icon -> !catalogIconFileNames.contains(icon))
        .toList();

    final List<String> errorMessages = List.of();

    if (!missingIcons.isEmpty()) {
      errorMessages.add("The following icon files have been referenced inside the seed files, but don't exist:\n\n" + String.join(", ", missingIcons));
    }

    if (!unusedIcons.isEmpty()) {
      errorMessages.add("The following icons are not used in the seed files and should be removed:\n\n" + String.join(", ", unusedIcons));
    }

    if (!errorMessages.isEmpty()) {
      throw new RuntimeException(String.join("\n\n", errorMessages));
    }
  }

}
