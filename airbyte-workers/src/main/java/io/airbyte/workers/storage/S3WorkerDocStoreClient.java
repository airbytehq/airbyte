package io.airbyte.workers.storage;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.util.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.helpers.LogConfigs;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import software.amazon.awssdk.core.ResponseBytes;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

public class S3WorkerDocStoreClient implements WorkerDocStoreClient {

  private final String bucketName;
  private final Path jobRoot;
  private final S3Client s3Client;

  public S3WorkerDocStoreClient(final S3Client s3Client, final String bucketName, final Path jobRoot) {
    this.s3Client = s3Client;
    this.bucketName = bucketName;
    this.jobRoot = jobRoot;
  }

  @Override
  public void write(final String id, final String document) {
    final PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(id)
        .build();

    s3Client.putObject(request, RequestBody.fromString(Jsons.serialize(document)));
  }

  @Override
  public String read(final String id) {
    final ResponseBytes<GetObjectResponse> objectAsBytes = s3Client.getObjectAsBytes(GetObjectRequest.builder().bucket(bucketName).key(id).build());
    return objectAsBytes.asString(StandardCharsets.UTF_8);
  }
}
