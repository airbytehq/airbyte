/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.ssh;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import java.io.IOException;
import java.io.StringReader;
import java.net.InetSocketAddress;
import java.security.KeyPair;
import java.util.List;
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
public class SshTunnel implements AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(SshTunnel.class);

  public enum TunnelMethod {
    NO_TUNNEL,
    SSH_PASSWORD_AUTH,
    SSH_KEY_AUTH
  }

  public static final int TIMEOUT_MILLIS = 15000; // 15 seconds

  private final JsonNode config;
  private final List<String> hostKey;
  private final List<String> portKey;

  private final TunnelMethod tunnelMethod;
  private final String tunnelHost;
  private final int tunnelPort;
  private final String tunnelUser;
  private final String sshKey;
  private final String tunnelUserPassword;
  private final String remoteDatabaseHost;
  private final int remoteDatabasePort;
  private int tunnelDatabasePort;

  private SshClient sshclient;
  private ClientSession tunnelSession;

  /**
   *
   * @param config - the full config that was passed to the source.
   * @param hostKey - a list of keys that point to the database host name. should be pointing to where
   *        in the config remoteDatabaseHost is found.
   * @param portKey - a list of keys that point to the database port. should be pointing to where in
   *        the config remoteDatabasePort is found.
   * @param tunnelMethod - the type of ssh method that should be used (includes not using SSH at all).
   * @param tunnelHost - host name of the machine to which we will establish an ssh connection (e.g.
   *        hostname of the bastion).
   * @param tunnelPort - port of the machine to which we will establish an ssh connection. (e.g. port
   *        of the bastion).
   * @param tunnelUser - user that is allowed to access the tunnelHost.
   * @param sshKey - the ssh key that will be used to make the ssh connection. can be null if we are
   *        using tunnelUserPassword instead.
   * @param tunnelUserPassword - the password for the tunnelUser. can be null if we are using sshKey
   *        instead.
   * @param remoteDatabaseHost - the actual host name of the database (as it is known to the tunnel
   *        host).
   * @param remoteDatabasePort - the actual port of the database (as it is known to the tunnel host).
   */
  public SshTunnel(final JsonNode config,
                   final List<String> hostKey,
                   final List<String> portKey,
                   final TunnelMethod tunnelMethod,
                   final String tunnelHost,
                   final int tunnelPort,
                   final String tunnelUser,
                   final String sshKey,
                   final String tunnelUserPassword,
                   final String remoteDatabaseHost,
                   final int remoteDatabasePort) {
    this.config = config;
    this.hostKey = hostKey;
    this.portKey = portKey;

    Preconditions.checkNotNull(tunnelMethod);
    this.tunnelMethod = tunnelMethod;

    if (tunnelMethod.equals(TunnelMethod.NO_TUNNEL)) {
      this.tunnelHost = null;
      this.tunnelPort = 0;
      this.tunnelUser = null;
      this.sshKey = null;
      this.tunnelUserPassword = null;
      this.remoteDatabaseHost = null;
      this.remoteDatabasePort = 0;
    } else {
      Preconditions.checkNotNull(tunnelHost);
      Preconditions.checkArgument(tunnelPort > 0);
      Preconditions.checkNotNull(tunnelUser);
      if (tunnelMethod.equals(TunnelMethod.SSH_KEY_AUTH)) {
        Preconditions.checkNotNull(sshKey);
      }
      if (tunnelMethod.equals(TunnelMethod.SSH_PASSWORD_AUTH)) {
        Preconditions.checkNotNull(tunnelUserPassword);
      }
      Preconditions.checkNotNull(remoteDatabaseHost);
      Preconditions.checkArgument(remoteDatabasePort > 0);

      this.tunnelHost = tunnelHost;
      this.tunnelPort = tunnelPort;
      this.tunnelUser = tunnelUser;
      this.sshKey = sshKey;
      this.tunnelUserPassword = tunnelUserPassword;
      this.remoteDatabaseHost = remoteDatabaseHost;
      this.remoteDatabasePort = remoteDatabasePort;

      this.sshclient = createClient();
      this.tunnelSession = openTunnel(sshclient);
    }
  }

  public JsonNode getOriginalConfig() {
    return config;
  }

  public JsonNode getConfigInTunnel() {
    if (tunnelMethod.equals(TunnelMethod.NO_TUNNEL)) {
      return getOriginalConfig();
    } else {
      final JsonNode clone = Jsons.clone(config);
      Jsons.replaceNestedString(clone, hostKey, SshdSocketAddress.LOCALHOST_ADDRESS.getHostName());
      Jsons.replaceNestedInt(clone, portKey, tunnelDatabasePort);
      return clone;
    }
  }

  // /**
  // * Finds a free port on the machine. As soon as this method returns, it is possible for process to
  // bind to this port. Thus it only gives a guarantee that at the time
  // */
  // private static int findFreePort() {
  // // finds an available port.
  // try (final var socket = new ServerSocket(0)) {
  // return socket.getLocalPort();
  // } catch (final IOException e) {
  // throw new RuntimeException(e);
  // }
  // }

  public static SshTunnel getInstance(final JsonNode config, final List<String> hostKey, final List<String> portKey) {
    final TunnelMethod tunnelMethod = Jsons.getOptional(config, "tunnel_method", "tunnel_method")
        .map(method -> TunnelMethod.valueOf(method.asText().trim()))
        .orElse(TunnelMethod.NO_TUNNEL);
    LOGGER.info("Starting connection with method: {}", tunnelMethod);

    // final int localPort = findFreePort();

    return new SshTunnel(
        config,
        hostKey,
        portKey,
        tunnelMethod,
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_host")),
        Jsons.getIntOrZero(config, "tunnel_method", "tunnel_port"),
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_user")),
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "ssh_key")),
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_user_password")),
        Strings.safeTrim(Jsons.getStringOrNull(config, hostKey)),
        Jsons.getIntOrZero(config, portKey));
  }

  public static void sshWrap(final JsonNode config,
                             final List<String> hostKey,
                             final List<String> portKey,
                             final CheckedConsumer<JsonNode, Exception> wrapped)
      throws Exception {
    sshWrap(config, hostKey, portKey, (configInTunnel) -> {
      wrapped.accept(configInTunnel);
      return null;
    });
  }

  public static <T> T sshWrap(final JsonNode config,
                              final List<String> hostKey,
                              final List<String> portKey,
                              final CheckedFunction<JsonNode, T, Exception> wrapped)
      throws Exception {
    try (final SshTunnel sshTunnel = SshTunnel.getInstance(config, hostKey, portKey)) {
      return wrapped.apply(sshTunnel.getConfigInTunnel());
    }
  }

  /**
   * Closes a tunnel if one was open, and otherwise doesn't do anything (safe to run).
   */
  @Override
  public void close() {
    try {
      if (tunnelSession != null) {
        tunnelSession.close();
        tunnelSession = null;
      }
      if (sshclient != null) {
        sshclient.stop();
        sshclient = null;
      }
    } catch (final Throwable t) {
      throw new RuntimeException(t);
    }
  }

  /**
   * From the RSA format private key string, use bouncycastle to deserialize the key pair, reconstruct
   * the keys from the key info, and return the key pair for use in authentication.
   */
  private KeyPair getPrivateKeyPair() throws IOException {
    final PEMParser pemParser = new PEMParser(new StringReader(validateKey()));
    final PEMKeyPair keypair = (PEMKeyPair) pemParser.readObject();
    final JcaPEMKeyConverter converter = new JcaPEMKeyConverter();
    return new KeyPair(
        converter.getPublicKey(SubjectPublicKeyInfo.getInstance(keypair.getPublicKeyInfo())),
        converter.getPrivateKey(keypair.getPrivateKeyInfo()));
  }

  private String validateKey() {
    return sshKey.replace("\\n", "\n");
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

  /**
   * Starts an ssh session; wrap this in a try-finally and use closeTunnel() to close it.
   */
  private ClientSession openTunnel(final SshClient client) {
    try {
      client.start();
      final ClientSession session = client.connect(
          tunnelUser.trim(),
          tunnelHost.trim(),
          tunnelPort)
          .verify(TIMEOUT_MILLIS)
          .getSession();
      if (tunnelMethod.equals(TunnelMethod.SSH_KEY_AUTH)) {
        session.addPublicKeyIdentity(getPrivateKeyPair());
      }
      if (tunnelMethod.equals(TunnelMethod.SSH_PASSWORD_AUTH)) {
        session.addPasswordIdentity(tunnelUserPassword);
      }

      session.auth().verify(TIMEOUT_MILLIS);
      final SshdSocketAddress address = session.startLocalPortForwarding(
          // entering 0 lets the OS pick a free port for us.
          new SshdSocketAddress(InetSocketAddress.createUnresolved(SshdSocketAddress.LOCALHOST_ADDRESS.getHostName(), 0)),
          new SshdSocketAddress(remoteDatabaseHost, remoteDatabasePort));

      // discover the port that the OS picked and remember it so that we can use it when we try to connect
      // later.
      tunnelDatabasePort = address.getPort();

      LOGGER.info("Established tunneling session.  Port forwarding started on " + address.toInetSocketAddress());
      return session;
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public String toString() {
    return "SshTunnel{" +
        "hostKey=" + hostKey +
        ", portKey=" + portKey +
        ", tunnelMethod=" + tunnelMethod +
        ", tunnelHost='" + tunnelHost + '\'' +
        ", tunnelPort=" + tunnelPort +
        ", tunnelUser='" + tunnelUser + '\'' +
        ", remoteDatabaseHost='" + remoteDatabaseHost + '\'' +
        ", remoteDatabasePort=" + remoteDatabasePort +
        ", tunnelDatabasePort=" + tunnelDatabasePort +
        '}';
  }

}
