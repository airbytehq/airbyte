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
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Simple task that checks if all icons in the seed definition files exist as well as that no icon
 * in the icons folder is unused.
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

    // remove all null values
    sourceIcons.removeAll(Collections.singleton(null));

    return sourceIcons;
  }

  private static List<String> difference(final List<String> list1, final List<String> list2) {
    List<String> difference = new ArrayList<>(list1);
    difference.removeAll(list2);
    return difference;
  }

  public static void main(final String[] args) throws Exception {
    final List<String> catalogIconFileNames = getIconFileNamesFromCatalog();
    final List<String> localIconFileNames = getLocalIconFileNames();

    final List<String> missingIcons = difference(catalogIconFileNames, localIconFileNames);
    final List<String> unusedIcons = difference(localIconFileNames, catalogIconFileNames);

    final List<String> errorMessages = List.of();
    if (!missingIcons.isEmpty()) {
      errorMessages
          .add("The following icon files have been referenced inside the seed files, but don't exist:\n\n" + String.join(", ", missingIcons));
    }

    if (!unusedIcons.isEmpty()) {
      errorMessages.add("The following icons are not used in the seed files and should be removed:\n\n" + String.join(", ", unusedIcons));
    }

    if (!errorMessages.isEmpty()) {
      throw new RuntimeException(String.join("\n\n", errorMessages));
    }
  }

}
