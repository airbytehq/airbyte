package io.airbyte.integrations.destination_async;

import java.text.DecimalFormat;

public class AirbyteFileUtils {
  private static final double ONE_KB = 1024;
  private static final double ONE_MB = ONE_KB * 1024;
  private static final double ONE_GB = ONE_MB * 1024;
  private static final double ONE_TB = ONE_GB * 1024;
  private static final DecimalFormat df = new DecimalFormat("#.##");


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
