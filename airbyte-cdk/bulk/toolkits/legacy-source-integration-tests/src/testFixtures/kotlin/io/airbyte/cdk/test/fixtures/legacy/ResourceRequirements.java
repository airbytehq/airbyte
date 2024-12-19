
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import java.io.Serializable;

/**
 * ResourceRequirements
 * <p>
 * generic configuration for pod source requirements
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "cpu_request",
    "cpu_limit",
    "memory_request",
    "memory_limit"
})
public class ResourceRequirements implements Serializable
{

    @JsonProperty("cpu_request")
    private String cpuRequest;
    @JsonProperty("cpu_limit")
    private String cpuLimit;
    @JsonProperty("memory_request")
    private String memoryRequest;
    @JsonProperty("memory_limit")
    private String memoryLimit;
    private final static long serialVersionUID = 4560234143748688189L;

    @JsonProperty("cpu_request")
    public String getCpuRequest() {
        return cpuRequest;
    }

    @JsonProperty("cpu_request")
    public void setCpuRequest(String cpuRequest) {
        this.cpuRequest = cpuRequest;
    }

    public ResourceRequirements withCpuRequest(String cpuRequest) {
        this.cpuRequest = cpuRequest;
        return this;
    }

    @JsonProperty("cpu_limit")
    public String getCpuLimit() {
        return cpuLimit;
    }

    @JsonProperty("cpu_limit")
    public void setCpuLimit(String cpuLimit) {
        this.cpuLimit = cpuLimit;
    }

    public ResourceRequirements withCpuLimit(String cpuLimit) {
        this.cpuLimit = cpuLimit;
        return this;
    }

    @JsonProperty("memory_request")
    public String getMemoryRequest() {
        return memoryRequest;
    }

    @JsonProperty("memory_request")
    public void setMemoryRequest(String memoryRequest) {
        this.memoryRequest = memoryRequest;
    }

    public ResourceRequirements withMemoryRequest(String memoryRequest) {
        this.memoryRequest = memoryRequest;
        return this;
    }

    @JsonProperty("memory_limit")
    public String getMemoryLimit() {
        return memoryLimit;
    }

    @JsonProperty("memory_limit")
    public void setMemoryLimit(String memoryLimit) {
        this.memoryLimit = memoryLimit;
    }

    public ResourceRequirements withMemoryLimit(String memoryLimit) {
        this.memoryLimit = memoryLimit;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(ResourceRequirements.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("cpuRequest");
        sb.append('=');
        sb.append(((this.cpuRequest == null)?"<null>":this.cpuRequest));
        sb.append(',');
        sb.append("cpuLimit");
        sb.append('=');
        sb.append(((this.cpuLimit == null)?"<null>":this.cpuLimit));
        sb.append(',');
        sb.append("memoryRequest");
        sb.append('=');
        sb.append(((this.memoryRequest == null)?"<null>":this.memoryRequest));
        sb.append(',');
        sb.append("memoryLimit");
        sb.append('=');
        sb.append(((this.memoryLimit == null)?"<null>":this.memoryLimit));
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
        result = ((result* 31)+((this.memoryRequest == null)? 0 :this.memoryRequest.hashCode()));
        result = ((result* 31)+((this.memoryLimit == null)? 0 :this.memoryLimit.hashCode()));
        result = ((result* 31)+((this.cpuLimit == null)? 0 :this.cpuLimit.hashCode()));
        result = ((result* 31)+((this.cpuRequest == null)? 0 :this.cpuRequest.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof ResourceRequirements) == false) {
            return false;
        }
        ResourceRequirements rhs = ((ResourceRequirements) other);
        return (((((this.memoryRequest == rhs.memoryRequest)||((this.memoryRequest!= null)&&this.memoryRequest.equals(rhs.memoryRequest)))&&((this.memoryLimit == rhs.memoryLimit)||((this.memoryLimit!= null)&&this.memoryLimit.equals(rhs.memoryLimit))))&&((this.cpuLimit == rhs.cpuLimit)||((this.cpuLimit!= null)&&this.cpuLimit.equals(rhs.cpuLimit))))&&((this.cpuRequest == rhs.cpuRequest)||((this.cpuRequest!= null)&&this.cpuRequest.equals(rhs.cpuRequest))));
    }

}
