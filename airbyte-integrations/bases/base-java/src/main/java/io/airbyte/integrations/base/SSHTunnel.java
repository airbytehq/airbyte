package io.airbyte.integrations.base;

import java.io.IOException;
import java.net.URISyntaxException;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;
import org.apache.sshd.client.SshClient;
import org.apache.sshd.client.session.ClientSession;
import org.apache.sshd.common.util.net.SshdSocketAddress;
import org.apache.sshd.server.forward.AcceptAllForwardingFilter;

/**
 * Encapsulates the connection configuration for an ssh tunnel port forward through a proxy/bastion host plus the remote host and remote port to
 * forward to a specified local port.
 */
public class SSHTunnel {

  public static final int TIMEOUT_MILLIS = 1000;
  private final String method;
  private final String host;
  private final String tunnelSshPort;
  private final String user;
  private final String sshkey;
  private final String password;
  private final String remoteDatabaseHost;
  private final String remoteDatabasePort;
  private final String tunnelDatabasePort;

  public SSHTunnel(String method, String host, String tunnelSshPort,
      String user, String sshkey, String password, String remoteDatabaseHost, String remoteDatabasePort, String tunnelDatabasePort) {
    this.method = method;
    this.host = host;
    this.tunnelSshPort = tunnelSshPort;
    this.user = user;
    this.sshkey = sshkey;
    this.password = password;
    this.remoteDatabaseHost = remoteDatabaseHost;
    this.remoteDatabasePort = remoteDatabasePort;
    this.tunnelDatabasePort = tunnelDatabasePort;
  }


  public String getMethod() {
    return method;
  }

  public String getHost() {
    return host;
  }

  public String getTunnelSshPort() {
    return tunnelSshPort;
  }

  public String getUser() {
    return user;
  }

  // TODO: Determine if we can lock down the access on credentials a bit tighter
  String getSSHKey() {
    return sshkey;
  }

  public String getPassword() {
    return password;
  }

  public String getRemoteDatabaseHost() {
    return remoteDatabaseHost;
  }

  public String getRemoteDatabasePort() {
    return remoteDatabasePort;
  }

  public String getTunnelDatabasePort() {
    return tunnelDatabasePort;
  }

  /**
   * From the pem format private key string, parse the private key, discover the public key, and return the pair for auth use.
   *
   * @return
   * @throws InvalidKeySpecException
   * @throws NoSuchAlgorithmException
   * @throws URISyntaxException
   */
  protected KeyPair getPrivateKeyPair() throws InvalidKeySpecException, NoSuchAlgorithmException {
    KeyFactory kf = KeyFactory.getInstance("RSA");
    // TODO: bouncycastle has a pem reader that can do this step for us.
    String privateKeyContent = getSSHKey().replaceAll("\\n", "").replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "");
    PrivateKey privKey = kf.generatePrivate(new PKCS8EncodedKeySpec(Base64.getDecoder().decode(privateKeyContent)));
    RSAPublicKey pubKey = (RSAPublicKey) kf.generatePublic(kf.getKeySpec(privKey, X509EncodedKeySpec.class));
    return new KeyPair(pubKey, privKey);
  }

  /**
   * Generates a new ssh client and returns it, with forwarding set to accept all types; use this before opening a tunnel.
   * @return
   */
  public SshClient createClient() {
    SshClient client = SshClient.setUpDefaultClient();
    client.setForwardingFilter(AcceptAllForwardingFilter.INSTANCE);
    return client;
  }

  /**
   * Starts an ssh session; wrap this in a try-finally and use closeTunnel() to close it.
   * @return
   * @throws IOException
   * @throws InvalidKeySpecException
   * @throws NoSuchAlgorithmException
   * @throws URISyntaxException
   */
  public ClientSession openTunnel(SshClient client) throws IOException, InvalidKeySpecException, NoSuchAlgorithmException {
    client.start();
    ClientSession session = client
        .connect(getUser(), getHost(), Integer.getInteger(getTunnelSshPort()))
        .verify(TIMEOUT_MILLIS)
        .getSession();
    session.addPasswordIdentity(getPassword());
    session.addPublicKeyIdentity(getPrivateKeyPair());
    session.auth().verify(TIMEOUT_MILLIS);
    session.startRemotePortForwarding(
        new SshdSocketAddress(getRemoteDatabaseHost(), Integer.getInteger(getRemoteDatabasePort())),
        new SshdSocketAddress("localhost", Integer.getInteger(getTunnelDatabasePort()))
    );
    return session;
  }

  public void closeTunnel(SshClient client, ClientSession session) throws IOException {
    session.close();
    client.stop();
  }

  @Override
  public String toString() {
    return "SSHTunnel{" +
        "method='" + method + '\'' +
        ", host='" + host + '\'' +
        ", tunnelSshPort='" + tunnelSshPort + '\'' +
        ", user='" + user + '\'' +
        ", remoteDatabaseHost='" + remoteDatabaseHost + '\'' +
        ", remoteDatabasePort='" + remoteDatabasePort + '\'' +
        ", tunnelDatabasePort='" + tunnelDatabasePort + '\'' +
        '}';
  }
}
