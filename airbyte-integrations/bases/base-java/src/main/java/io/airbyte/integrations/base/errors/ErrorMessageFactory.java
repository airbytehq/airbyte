package io.airbyte.integrations.base.errors;

import io.airbyte.integrations.base.errors.messages.ErrorMessage;
import io.airbyte.integrations.base.errors.messages.MsSQLErrorMessage;
import io.airbyte.integrations.base.errors.messages.MySQLErrorMessage;
import io.airbyte.integrations.base.errors.messages.NoImplementErrorMessage;
import io.airbyte.integrations.base.errors.messages.PostgresErrorMessage;
import io.airbyte.integrations.base.errors.utils.ConnectorType;

import java.util.Map;

import static io.airbyte.integrations.base.errors.utils.ConnectorType.MS_SQL;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.MY_SQL;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.POSTGRES;

public class ErrorMessageFactory {

    private final static Map<ConnectorType, ErrorMessage> MAP = Map.of(MS_SQL, new MsSQLErrorMessage(),
            MY_SQL, new MySQLErrorMessage(),
            POSTGRES, new PostgresErrorMessage(),
            ConnectorType.DEFAULT, new NoImplementErrorMessage());

    public static ErrorMessage getErrorMessage(ConnectorType type) {
        if (MAP.containsKey(type)) {
            return MAP.get(type);
        }
        return MAP.get(ConnectorType.DEFAULT);
    }
}
