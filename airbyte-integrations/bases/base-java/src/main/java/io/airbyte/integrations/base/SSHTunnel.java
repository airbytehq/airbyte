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
import com.google.common.base.Preconditions;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.io.StringReader;
import java.security.KeyPair;
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

// todo (cgardens) - this needs unit tests. it is currently tested transitively via source postgres
// integration tests.
/**
 * Encapsulates the connection configuration for an ssh tunnel port forward through a proxy/bastion
 * host plus the remote host and remote port to forward to a specified local port.
 */
public class SSHTunnel implements AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(SSHTunnel.class);

  public enum Method {
    NO_TUNNEL,
    SSH_PASSWORD_AUTH,
    SSH_KEY_AUTH
  }

  public static final int TIMEOUT_MILLIS = 15000; // 15 seconds
  private final Method method;
  private final String host;
  private final String tunnelSshPort;
  private final String user;
  private final String sshkey;
  private final String password;
  private final String remoteDatabaseHost;
  private final String remoteDatabasePort;
  private final String tunnelDatabasePort;

  private SshClient sshclient;
  private ClientSession tunnelSession;

  public SSHTunnel(final Method method,
                   final String host,
                   final String tunnelSshPort,
                   final String user,
                   final String sshKey,
                   final String password,
                   final String remoteDatabaseHost,
                   final String remoteDatabasePort,
                   final String tunnelDatabasePort) {

    Preconditions.checkNotNull(method);
    this.method = method;

    if (method.equals(Method.NO_TUNNEL)) {
      this.host = null;
      this.tunnelSshPort = null;
      this.user = null;
      this.sshkey = null;
      this.password = null;
      this.remoteDatabaseHost = null;
      this.remoteDatabasePort = null;
      this.tunnelDatabasePort = null;
    } else {
      Preconditions.checkNotNull(host);
      Preconditions.checkNotNull(tunnelSshPort);
      Preconditions.checkNotNull(user);
      Preconditions.checkArgument(sshKey != null || password != null,
          "SSH Tunnel was requested to be opened while it was already open.  This is a coding error.");
      Preconditions.checkNotNull(remoteDatabaseHost);
      Preconditions.checkNotNull(remoteDatabasePort);
      Preconditions.checkNotNull(tunnelDatabasePort);

      this.host = host;
      this.tunnelSshPort = tunnelSshPort;
      this.user = user;
      this.sshkey = sshKey;
      this.password = password;
      this.remoteDatabaseHost = remoteDatabaseHost;
      this.remoteDatabasePort = remoteDatabasePort;
      this.tunnelDatabasePort = tunnelDatabasePort;

      this.sshclient = createClient();
      this.tunnelSession = openTunnel(sshclient);
    }
  }

  public static SSHTunnel getInstance(final JsonNode config) {
    final JsonNode sshConfig = config.get("tunnel_method");
    final Method tunnelMethod = Method.valueOf(Jsons.getStringOrNull(sshConfig, "tunnel_method").trim());
    LOGGER.info("Starting connection with method: {}", tunnelMethod);

    return new SSHTunnel(
        tunnelMethod,
        Jsons.getStringOrNull(sshConfig, "tunnel_host").trim(),
        Jsons.getStringOrNull(sshConfig, "tunnel_ssh_port").trim(),
        Jsons.getStringOrNull(sshConfig, "tunnel_username").trim(),
        Jsons.getStringOrNull(sshConfig, "tunnel_usersshkey").trim(),
        Jsons.getStringOrNull(sshConfig, "tunnel_userpass").trim(),
        Jsons.getStringOrNull(sshConfig, "tunnel_db_remote_host").trim(),
        Jsons.getStringOrNull(sshConfig, "tunnel_db_remote_port").trim(),
        Jsons.getStringOrNull(sshConfig, "tunnel_localport").trim());
  }

  public static void sshWrap(final JsonNode config, final VoidCallable wrapped) throws Exception {
    sshWrap(config, () -> {
      wrapped.call();
      return null;
    });
  }

  public static <T> T sshWrap(final JsonNode config, final CheckedSupplier<T, Exception> wrapped) throws Exception {
    try (final SSHTunnel ignored = SSHTunnel.getInstance(config)) {
      return wrapped.get();
    }
  }

  /**
   * Closes a tunnel if one was open, and otherwise doesn't do anything (safe to run).
   */
  @Override
  public void close() {
    try {
      if (shouldTunnel()) {
        if (tunnelSession != null) {
          tunnelSession.close();
          tunnelSession = null;
        }
        if (sshclient != null) {
          sshclient.stop();
          sshclient = null;
        }
      }
    } catch (final Throwable t) {
      throw new RuntimeException(t);
    }
  }

  public boolean shouldTunnel() {
    return method != null && !"NO_TUNNEL".equals(method);
  }

  /**
   * From the RSA format private key string, use bouncycastle to deserialize the key pair, reconstruct
   * the keys from the key info, and return the key pair for use in authentication.
   */
  private KeyPair getPrivateKeyPair() throws IOException {
    final PEMParser pemParser = new PEMParser(new StringReader(sshkey));
    final PEMKeyPair keypair = (PEMKeyPair) pemParser.readObject();
    final JcaPEMKeyConverter converter = new JcaPEMKeyConverter();
    return new KeyPair(
        converter.getPublicKey(SubjectPublicKeyInfo.getInstance(keypair.getPublicKeyInfo())),
        converter.getPrivateKey(keypair.getPrivateKeyInfo()));
  }

  /**
   * Generates a new ssh client and returns it, with forwarding set to accept all types; use this
   * before opening a tunnel.
   */
  private SshClient createClient() {
    java.security.Security.addProvider(
        new org.bouncycastle.jce.provider.BouncyCastleProvider());
    final SshClient client = SshClient.setUpDefaultClient();
    client.setForwardingFilter(AcceptAllForwardingFilter.INSTANCE);
    client.setServerKeyVerifier(AcceptAllServerKeyVerifier.INSTANCE);
    return client;
  }

  private void validate() {
    Preconditions.checkNotNull(host, "SSH Tunnel host is null - verify configuration before starting tunnel!");
  }

  /**
   * Starts an ssh session; wrap this in a try-finally and use closeTunnel() to close it.
   */
  private ClientSession openTunnel(final SshClient client) {
    try {
      validate();
      client.start();
      final ClientSession session = client.connect(
          user.trim(),
          host.trim(),
          Integer.parseInt(tunnelSshPort.trim())).verify(TIMEOUT_MILLIS)
          .getSession();
      if (method.equals("SSH_KEY_AUTH")) {
        session.addPublicKeyIdentity(getPrivateKeyPair());
      }
      if (method.equals("SSH_PASSWORD_AUTH")) {
        session.addPasswordIdentity(password);
      }
      session.auth().verify(TIMEOUT_MILLIS);
      final SshdSocketAddress address = session.startLocalPortForwarding(
          new SshdSocketAddress(SshdSocketAddress.LOCALHOST_ADDRESS.getHostName(), Integer.parseInt(tunnelDatabasePort.trim())),
          new SshdSocketAddress(remoteDatabaseHost.trim(), Integer.parseInt(remoteDatabasePort.trim())));
      LOGGER.info("Established tunneling session.  Port forwarding started on " + address.toInetSocketAddress());
      return session;
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
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
