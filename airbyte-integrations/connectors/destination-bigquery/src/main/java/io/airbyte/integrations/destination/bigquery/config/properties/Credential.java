package io.airbyte.integrations.destination.bigquery.config.properties;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Map;

public class Credential {

    @JsonProperty("credential_type")
    private final String credentialType;
    @JsonProperty("hmac_key_access_id")
    private final String hmacKeyAccessId;
    @JsonProperty("hmac_key_secret")
    private final String hmacKeySecret;

    public Credential(final Map<String,String> credential) {
        this.credentialType = credential.get("credential-type");
        this.hmacKeyAccessId = credential.get("hmac-key-access-id");
        this.hmacKeySecret = credential.get("hmac-key-secret");
    }

    public String getCredentialType() {
        return credentialType;
    }

    public String getHmacKeyAccessId() {
        return hmacKeyAccessId;
    }

    public String getHmacKeySecret() {
        return hmacKeySecret;
    }

    @Override
    public String toString() {
        return "Credential{" +
                "credentialType='" + credentialType + '\'' +
                ", hmacKeyAccessId='" + hmacKeyAccessId + '\'' +
                ", hmacKeySecret='" + hmacKeySecret + '\'' +
                '}';
    }

}