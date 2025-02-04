
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonValue;
import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;

/**
 * OperatorNormalization
 * <p>
 * Settings for a normalization operator
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "option"
})
public class OperatorNormalization implements Serializable
{

    @JsonProperty("option")
    private Option option;
    private final static long serialVersionUID = 7237719528722425365L;

    @JsonProperty("option")
    public Option getOption() {
        return option;
    }

    @JsonProperty("option")
    public void setOption(Option option) {
        this.option = option;
    }

    public OperatorNormalization withOption(Option option) {
        this.option = option;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(OperatorNormalization.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("option");
        sb.append('=');
        sb.append(((this.option == null)?"<null>":this.option));
        sb.append(',');
        if (sb.charAt((sb.length()- 1)) == ',') {
            sb.setCharAt((sb.length()- 1), ']');
        } else {
            sb.append(']');
        }
        return sb.toString();
    }

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.option == null)? 0 :this.option.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof OperatorNormalization) == false) {
            return false;
        }
        OperatorNormalization rhs = ((OperatorNormalization) other);
        return ((this.option == rhs.option)||((this.option!= null)&&this.option.equals(rhs.option)));
    }

    public enum Option {

        BASIC("basic");
        private final String value;
        private final static Map<String, Option> CONSTANTS = new HashMap<String, Option>();

        static {
            for (Option c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        private Option(String value) {
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
        public static Option fromValue(String value) {
            Option constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}
