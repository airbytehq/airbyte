package io.airbyte.integrations.util;

import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.integrations.base.errors.messages.ErrorMessage;

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.function.Predicate;

public class ConnectorExceptionUtil {

    private static final List<Predicate<Throwable>> configErrorPredicates = new ArrayList<>();
    private static final String RECOVERY_CONNECTION_ERROR_MESSAGE = "We're having issues syncing from a Postgres replica that is configured as a hot standby server. " +
            "Please see https://docs.airbyte.com/integrations/sources/postgres/#sync-data-from-postgres-hot-standby-server for options and workarounds";

    static {
        configErrorPredicates.add(getConfigErrorPredicate());
        configErrorPredicates.add(getConnectionErrorPredicate());
        configErrorPredicates.add(isRecoveryConnectionExceptionPredicate());
    }

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
        } else {
            return String.format("Could not connect with provided configuration. Error: %s", e.getMessage() != null ? e.getMessage() : "");
        }
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
}
