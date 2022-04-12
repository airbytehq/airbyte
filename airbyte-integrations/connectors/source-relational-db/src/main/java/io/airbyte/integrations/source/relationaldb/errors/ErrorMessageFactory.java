package io.airbyte.integrations.source.relationaldb.errors;

import java.util.HashMap;
import java.util.Map;
import java.util.ServiceLoader;

import static io.airbyte.db.exception.CustomExceptionUtils.NO_IMPLEMENTED_YET;

public class ErrorMessageFactory {

    private final static Map<String, ErrorMessage> MAP = new HashMap<>();

    static {
        ServiceLoader<ErrorMessage> loader = ServiceLoader.load(ErrorMessage.class);
        for (ErrorMessage implClass : loader) {
            MAP.put(implClass.getConnectorType(), implClass);
        }
    }

    public static ErrorMessage getErrorMessage(String type) {
        if (MAP.containsKey(type)) {
            return MAP.get(type);
        }
        return MAP.get(NO_IMPLEMENTED_YET);
    }
}
