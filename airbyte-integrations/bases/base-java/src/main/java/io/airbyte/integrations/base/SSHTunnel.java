/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.IOException;
import java.io.StringReader;
import java.net.URISyntaxException;
import java.security.KeyPair;
import java.security.NoSuchAlgorithmException;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.InvalidKeySpecException;
import org.apache.sshd.client.SshClient;
import org.apache.sshd.client.keyverifier.AcceptAllServerKeyVerifier;
import org.apache.sshd.client.session.ClientSession;
import org.apache.sshd.common.util.net.SshdSocketAddress;
import org.apache.sshd.server.forward.AcceptAllForwardingFilter;
import org.bouncycastle.asn1.x509.SubjectPublicKeyInfo;
import org.bouncycastle.openssl.PEMKeyPair;
import org.bouncycastle.openssl.PEMParser;
import org.bouncycastle.openssl.jcajce.JcaPEMKeyConverter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Encapsulates the connection configuration for an ssh tunnel port forward through a proxy/bastion
 * host plus the remote host and remote port to forward to a specified local port.
 */
public class SSHTunnel {

  private static final Logger LOGGER = LoggerFactory.getLogger(SSHTunnel.class);

  public static final int TIMEOUT_MILLIS = 15000; // 15 seconds
  private final String method;
  private final String host;
  private final String tunnelSshPort;
  private final String user;
  private final String sshkey;
  private final String password;
  private final String remoteDatabaseHost;
  private final String remoteDatabasePort;
  private final String tunnelDatabasePort;

  private SSHTunnel tunnelConfig = null;
  private SshClient sshclient = null;
  private ClientSession tunnelSession = null;

  public SSHTunnel(String method,
                   String host,
                   String tunnelSshPort,
                   String user,
                   String sshkey,
                   String password,
                   String remoteDatabaseHost,
                   String remoteDatabasePort,
                   String tunnelDatabasePort) {
    if (method == null) {
      this.method = "NO_TUNNEL";
    } else {
      this.method = method;
    }
    this.host = host;
    this.tunnelSshPort = tunnelSshPort;
    this.user = user;
    this.sshkey = sshkey;
    this.password = password;
    this.remoteDatabaseHost = remoteDatabaseHost;
    this.remoteDatabasePort = remoteDatabasePort;
    this.tunnelDatabasePort = tunnelDatabasePort;
  }

  public static SSHTunnel getInstance(JsonNode config) {
    JsonNode ourConfig = config.get("tunnel_method");
    SSHTunnel sshconfig = new SSHTunnel(
        getConfigValueOrNull(ourConfig, "tunnel_method"),
        getConfigValueOrNull(ourConfig, "tunnel_host"),
        getConfigValueOrNull(ourConfig, "tunnel_ssh_port"),
        getConfigValueOrNull(ourConfig, "tunnel_username"),
        getConfigValueOrNull(ourConfig, "tunnel_usersshkey"),
        getConfigValueOrNull(ourConfig, "tunnel_userpass"),
        getConfigValueOrNull(ourConfig, "tunnel_db_remote_host"),
        getConfigValueOrNull(ourConfig, "tunnel_db_remote_port"),
        getConfigValueOrNull(ourConfig, "tunnel_localport"));
    return sshconfig;
  }

  static String getConfigValueOrNull(JsonNode config, String key) {
    return config != null && config.has(key) ? config.get(key).asText() : null;
  }

  /**
   * Starts an ssh session; wrap this in a try-finally and use closeTunnel() to close it.
   *
   * @throws IOException
   */
  public void openTunnelIfRequested() throws IOException {
    if (shouldTunnel()) {
      try {
        throw new Exception("Troubleshooting JENNY");
      } catch (Exception e) {
        LOGGER.error("Troubleshooting! ", e);
      }
      if (tunnelSession != null || sshclient != null) {
        throw new RuntimeException("SSH Tunnel was requested to be opened while it was already open.  This is a coding error.");
      }
      sshclient = createClient();
      tunnelSession = openTunnel(sshclient);
    }
  }

  /**
   * Closes a tunnel if one was open, and otherwise doesn't do anything (safe to run).
   */
  public void closeTunnel() {
    try {
      if (shouldTunnel()) {
        if (tunnelSession != null) {
          tunnelSession.close();
        }
        if (sshclient != null) {
          sshclient.stop();
        }
        tunnelSession = null;
        sshclient = null;
      }
    } catch (Throwable t) {
      throw new RuntimeException(t);
    }
  }

  public boolean shouldTunnel() {
    return method != null && !"NO_TUNNEL".equals(method);
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

  private String getSSHKey() {
    return sshkey;
  }

  private String getPassword() {
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
   * From the RSA format private key string, use bouncycastle to deserialize the key pair, reconstruct
   * the keys from the key info, and return the key pair for use in authentication.
   *
   * @return
   * @throws IOException
   */
  private KeyPair getPrivateKeyPair() throws IOException {
    PEMParser pemParser = new PEMParser(new StringReader(getSSHKey()));
    PEMKeyPair keypair = (PEMKeyPair) pemParser.readObject();
    JcaPEMKeyConverter converter = new JcaPEMKeyConverter();
    return new KeyPair(
        (RSAPublicKey) converter.getPublicKey(SubjectPublicKeyInfo.getInstance(keypair.getPublicKeyInfo())),
        (RSAPrivateKey) converter.getPrivateKey(keypair.getPrivateKeyInfo()));
  }

  /**
   * Generates a new ssh client and returns it, with forwarding set to accept all types; use this
   * before opening a tunnel.
   *
   * @return
   */
  private SshClient createClient() {
    java.security.Security.addProvider(
        new org.bouncycastle.jce.provider.BouncyCastleProvider());
    SshClient client = SshClient.setUpDefaultClient();
    client.setForwardingFilter(AcceptAllForwardingFilter.INSTANCE);
    client.setServerKeyVerifier(AcceptAllServerKeyVerifier.INSTANCE);
    return client;
  }

  private void validate() {
    if (getHost() == null) {
      throw new RuntimeException("SSH Tunnel host is null - verify configuration before starting tunnel!");
    }
  }

  /**
   * Starts an ssh session; wrap this in a try-finally and use closeTunnel() to close it.
   *
   * @return
   * @throws IOException
   * @throws InvalidKeySpecException
   * @throws NoSuchAlgorithmException
   * @throws URISyntaxException
   */
  private ClientSession openTunnel(SshClient client) throws IOException {
    validate();
    client.start();
    ClientSession session = client.connect(
        getUser().trim(),
        getHost().trim(),
        Integer.parseInt(
            getTunnelSshPort().trim()))
        .verify(TIMEOUT_MILLIS)
        .getSession();
    if (getMethod().equals("SSH_KEY_AUTH")) {
      session.addPublicKeyIdentity(getPrivateKeyPair());
    }
    if (getMethod().equals("SSH_PASSWORD_AUTH")) {
      session.addPasswordIdentity(getPassword());
    }
    session.auth().verify(TIMEOUT_MILLIS);
    SshdSocketAddress address = session.startLocalPortForwarding(
        new SshdSocketAddress(SshdSocketAddress.LOCALHOST_ADDRESS.getHostName(), Integer.parseInt(getTunnelDatabasePort().trim())),
        new SshdSocketAddress(getRemoteDatabaseHost().trim(), Integer.parseInt(getRemoteDatabasePort().trim())));
    LOGGER.info("Established tunneling session.  Port forwarding started on " + address.toInetSocketAddress());
    return session;
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
