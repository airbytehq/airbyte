package io.airbyte.integrations.destination.elasticsearch;

import java.io.ByteArrayInputStream;
import java.security.KeyStore;
import java.security.cert.Certificate;
import java.security.cert.CertificateFactory;
import javax.net.ssl.SSLContext;
import org.apache.http.ssl.SSLContextBuilder;
import org.apache.http.ssl.SSLContexts;

public class SslUtils {

  public static SSLContext createContextFromCaCert(byte[] certAsBytes) {
    try {
      CertificateFactory factory = CertificateFactory.getInstance("X.509");
      Certificate trustedCa = factory.generateCertificate(
          new ByteArrayInputStream(certAsBytes)
      );
      KeyStore trustStore = KeyStore.getInstance("pkcs12");
      trustStore.load(null, null);
      trustStore.setCertificateEntry("ca", trustedCa);
      SSLContextBuilder sslContextBuilder =
          SSLContexts.custom().loadTrustMaterial(trustStore, null);
      return sslContextBuilder.build();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

}
