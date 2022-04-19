package io.airbyte.integrations.destination.s3.signer;

import com.amazonaws.SignableRequest;
import com.amazonaws.auth.AWS4Signer;
import com.amazonaws.auth.AWSCredentials;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

public class CustomGCPSigner extends AWS4Signer {

  private static final Map<String, String> awsgcpHeaderMap = new HashMap<>() {{
    put("x-amz-storage-class", "x-goog-storage-class");
    put("x-amz-date", "x-goog-date");
    put("x-amz-copy-source", "x-goog-copy-source");
    put("x-amz-metadata-directive", "x-goog-metadata-directive");
    put("x-amz-copy-source-if-match", "x-goog-copy-source-if-none-match");
    put("x-amz-copy-source-if-unmodified-since", "x-goog-copy-source-if-unmodified-since");
    put("x-amz-copy-source-if-modified-since", "x-goog-copy-source-if-modified-since");
  }};

  private static <K, V> Map<K, V> clone(Map<K, V> original) {
    return original.entrySet()
        .stream()
        .collect(Collectors.toMap(Map.Entry::getKey,
            Map.Entry::getValue));
  }

  @Override
  public void sign(SignableRequest<?> request, AWSCredentials credentials) {
    request.addHeader("Authorization", "Bearer " + credentials.getAWSAccessKeyId());

    Map<String, String> headerCopy = clone(request.getHeaders());

    for (Map.Entry<String, String> entry : headerCopy.entrySet()) {

      if (awsgcpHeaderMap.containsKey(entry.getKey().toLowerCase())) {
        request.addHeader(awsgcpHeaderMap.get(entry.getKey()), entry.getValue());
      }

      if (entry.getKey().toLowerCase().startsWith("x-amz-meta-")) {
        String keyName = entry.getKey();
        String newKeyName = keyName.replace("x-amz-meta-", "x-goog-meta-");
        request.addHeader(newKeyName, entry.getValue());
      }
    }
  }
}
