/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb.utils;

import java.util.regex.Pattern;

public class ResponseUtils {

  public static final Pattern LABEL_EXIST_PATTERN =
      Pattern.compile("errCode = 2, detailMessage = Label \\[(.*)\\] " +
          "has already been used, relate to txn \\[(\\d+)\\]");

  public static final Pattern COMMITTED_PATTERN =
      Pattern.compile("errCode = 2, detailMessage = No files can be copied, matched (\\d+) files, " +
          "filtered (\\d+) files because files may be loading or loaded");

  public static final String RETRY_COMMIT = "submit task failed, queue size is full: SQL submitter with block policy";

  private ResponseUtils() {}

  public static boolean isCommitted(String msg) {
    return COMMITTED_PATTERN.matcher(msg).matches();
  }

}
