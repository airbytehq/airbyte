
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;
import java.util.HashMap;
import java.util.Map;

/**
 * ActorType
 * <p>
 * enum that describes different types of actors
 * 
 */
public enum ActorType {

    SOURCE("source"),
    DESTINATION("destination");
    private final String value;
    private final static Map<String, ActorType> CONSTANTS = new HashMap<String, ActorType>();

    static {
        for (ActorType c: values()) {
            CONSTANTS.put(c.value, c);
        }
    }

    private ActorType(String value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return this.value;
    }

    @JsonValue
    public String value() {
        return this.value;
    }

    @JsonCreator
    public static ActorType fromValue(String value) {
        ActorType constant = CONSTANTS.get(value);
        if (constant == null) {
            throw new IllegalArgumentException(value);
        } else {
            return constant;
        }
    }

}
