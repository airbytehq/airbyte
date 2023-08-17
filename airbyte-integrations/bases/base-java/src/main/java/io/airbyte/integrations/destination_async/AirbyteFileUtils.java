/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import java.text.DecimalFormat;

/**
 * Replicate the behavior of {@link org.apache.commons.io.FileUtils} to match the proclivities of
 * Davin and Charles. Courteously written by ChatGPT.
 */
public class AirbyteFileUtils {

  private static final double ONE_KB = 1024;
  private static final double ONE_MB = ONE_KB * 1024;
  private static final double ONE_GB = ONE_MB * 1024;
  private static final double ONE_TB = ONE_GB * 1024;
  private static final DecimalFormat df = new DecimalFormat("#.##");

  /**
   * Replicate the behavior of {@link org.apache.commons.io.FileUtils} but instead of rounding down to
   * the nearest whole number, it rounds to two decimal places.
   *
   * @param sizeInBytes size in bytes
   * @return human-readable size
   */
  public static String byteCountToDisplaySize(final long sizeInBytes) {

    if (sizeInBytes < ONE_KB) {
      return df.format(sizeInBytes) + " bytes";
    } else if (sizeInBytes < ONE_MB) {
      return df.format((double) sizeInBytes / ONE_KB) + " KB";
    } else if (sizeInBytes < ONE_GB) {
      return df.format((double) sizeInBytes / ONE_MB) + " MB";
    } else if (sizeInBytes < ONE_TB) {
      return df.format((double) sizeInBytes / ONE_GB) + " GB";
    } else {
      return df.format((double) sizeInBytes / ONE_TB) + " TB";
    }
  }

}
