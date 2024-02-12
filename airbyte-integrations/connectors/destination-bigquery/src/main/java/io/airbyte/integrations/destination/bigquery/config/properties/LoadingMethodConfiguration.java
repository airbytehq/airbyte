package io.airbyte.integrations.destination.bigquery.config.properties;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Map;

public class LoadingMethodConfiguration {

    @JsonProperty("method")
    private final String method;
    @JsonProperty("gcs_bucket_name")
    private final String gcsBucketName;
    @JsonProperty("gcs_bucket_path")
    private final String gcsBucketPath;
    @JsonProperty("credential")
    private final Credential credential;
    @JsonProperty("keep_files_in_gcs-bucket")
    private final String keepFilesInGcsBucket;

    public LoadingMethodConfiguration(final String method, final String gcsBucketName, final String gcsBucketPath, final Credential credential, final String keepFilesInGcsBucket) {
        this.method = method;
        this.gcsBucketName = gcsBucketName;
        this.gcsBucketPath = gcsBucketPath;
        this.credential = credential;
        this.keepFilesInGcsBucket = keepFilesInGcsBucket;
    }

    public String getMethod() {
        return method;
    }

    public String getGcsBucketName() {
        return gcsBucketName;
    }

    public String getGcsBucketPath() {
        return gcsBucketPath;
    }

    public Credential getCredential() {
        return credential;
    }

    public String getKeepFilesInGcsBucket() {
        return keepFilesInGcsBucket;
    }

    public static class Builder {
        private String method;
        private String gcsBucketName;
        private String gcsBucketPath;
        private Credential credential;
        private String keepFilesInGcsBucket;

        public Builder withCredential(final Map<String,String> credential) {
            this.credential = new Credential(credential);
            return this;
        }

        public Builder withKeepFilesInGcsBucket(final String keepFilesInGcsBucket) {
            this.keepFilesInGcsBucket = keepFilesInGcsBucket;
            return this;
        }

        public Builder withGcsBucketName(final String gcsBucketName) {
            this.gcsBucketName = gcsBucketName;
            return this;
        }

        public Builder withGcsBucketPath(final String gcsBucketPath) {
            this.gcsBucketPath = gcsBucketPath;
            return this;
        }

        public Builder withMethod(final String method) {
            this.method = method;
            return this;
        }

        public LoadingMethodConfiguration build() {
            return new LoadingMethodConfiguration(method, gcsBucketName, gcsBucketPath, credential, keepFilesInGcsBucket);
        }

    }

}
