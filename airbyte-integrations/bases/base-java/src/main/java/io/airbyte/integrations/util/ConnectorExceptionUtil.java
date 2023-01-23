/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util;

import com.google.common.collect.ImmutableList;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.integrations.base.errors.messages.ErrorMessage;
import java.sql.SQLException;
import java.sql.SQLSyntaxErrorException;
import java.util.List;
import java.util.Locale;
import java.util.function.Predicate;

/**
 * Utility class defining methods for handling configuration exceptions in connectors.
 */
public class ConnectorExceptionUtil {

  public static final String COMMON_EXCEPTION_MESSAGE_TEMPLATE = "Could not connect with provided configuration. Error: %s";
  static final String RECOVERY_CONNECTION_ERROR_MESSAGE =
      "We're having issues syncing from a Postgres replica that is configured as a hot standby server. " +
          "Please see https://docs.airbyte.com/integrations/sources/postgres/#sync-data-from-postgres-hot-standby-server for options and workarounds";

  public static final List<Integer> HTTP_AUTHENTICATION_ERROR_CODES = ImmutableList.of(401, 403);
  private static final List<Predicate<Throwable>> configErrorPredicates =
      List.of(getConfigErrorPredicate(), getConnectionErrorPredicate(),
          isRecoveryConnectionExceptionPredicate(), isUnknownColumnInFieldListException());

  public static boolean isConfigError(final Throwable e) {
    return configErrorPredicates.stream().anyMatch(predicate -> predicate.test(e));
  }

  public static String getDisplayMessage(final Throwable e) {
    if (e instanceof ConfigErrorException) {
      return ((ConfigErrorException) e).getDisplayMessage();
    } else if (e instanceof ConnectionErrorException) {
      final ConnectionErrorException connEx = (ConnectionErrorException) e;
      return ErrorMessage.getErrorMessage(connEx.getStateCode(), connEx.getErrorCode(), connEx.getExceptionMessage(), connEx);
    } else if (isRecoveryConnectionExceptionPredicate().test(e)) {
      return RECOVERY_CONNECTION_ERROR_MESSAGE;
    } else if (isUnknownColumnInFieldListException().test(e)) {
      return e.getMessage();
    } else {
      return String.format(COMMON_EXCEPTION_MESSAGE_TEMPLATE, e.getMessage() != null ? e.getMessage() : "");
    }
  }

  /**
   * Returns the first instance of an exception associated with a configuration error (if it exists).
   * Otherwise, the original exception is returned.
   */
  public static Throwable getRootConfigError(final Exception e) {
    Throwable current = e;
    while (current != null) {
      if (ConnectorExceptionUtil.isConfigError(current)) {
        return current;
      } else {
        current = current.getCause();
      }
    }
    return e;
  }

  private static Predicate<Throwable> getConfigErrorPredicate() {
    return e -> e instanceof ConfigErrorException;
  }

  private static Predicate<Throwable> getConnectionErrorPredicate() {
    return e -> e instanceof ConnectionErrorException;
  }

  private static Predicate<Throwable> isRecoveryConnectionExceptionPredicate() {
    return e -> e instanceof SQLException && e.getMessage()
        .toLowerCase(Locale.ROOT)
        .contains("due to conflict with recovery");
  }

  private static Predicate<Throwable> isUnknownColumnInFieldListException() {
    return e -> e instanceof SQLSyntaxErrorException
        && e.getMessage()
            .toLowerCase(Locale.ROOT)
            .contains("unknown column")
        && e.getMessage()
            .toLowerCase(Locale.ROOT)
            .contains("in 'field list'");
  }

}
