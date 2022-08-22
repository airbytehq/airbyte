/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.ssh;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.base.ssh.SshTunnel.TunnelMethod;
import java.util.Arrays;
import java.nio.charset.StandardCharsets;
import java.security.KeyPair;
import java.security.PrivateKey;
import java.security.PublicKey;
import org.apache.sshd.common.util.security.SecurityUtils;
import org.apache.sshd.common.util.security.eddsa.EdDSASecurityProviderRegistrar;
import org.junit.jupiter.api.Test;

class SshTunnelTest {

  private static final String OPENSSH_PRIVATE_KEY =
      "-----BEGIN OPENSSH PRIVATE KEY-----\\nb3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn\\nNhAAAAAwEAAQAAAYEAuFjfTMS6BrgoxaQe9i83y6CdGH3xJIwc1Wy+11ibWAFcQ6khX/x0\\nM+JnJaSCs/hxiDE4afHscP3HzVQC699IgKwyAPaG0ZG+bLhxWAm4E79P7Yssj7imhTqr0A\\nDZDO23CCOagHvfdg1svnBhk1ih14GMGKRFCS27CLgholIOeogOyH7b3Jaqy9LtICiE054e\\njwdaZdwWU08kxMO4ItdxNasCPC5uQiaXIzWFysG0mLk7WWc8WyuQHneQFl3Qu6p/rWJz4i\\nseea5CBL5s1DIyCyo/jgN5/oOWOciPUl49mDLleCzYTDnWqX43NK9A87unNeuA95Fk9akH\\n8QH4hKBCzpHhsh4U3Ys/l9Q5NmnyBrtFWBY2n13ZftNA/Ms+Hsh6V3eyJW0rIFY2/UM4XA\\nYyD6MEOlvFAQjxC6EbqfkrC6FQgH3I2wAtIDqEk2j79vfIIDdzp8otWjIQsApX55j+kKio\\nsY8YTXb9sLWuEdpSd/AN3iQ8HwIceyTulaKn7rTBAAAFkMwDTyPMA08jAAAAB3NzaC1yc2\\nEAAAGBALhY30zEuga4KMWkHvYvN8ugnRh98SSMHNVsvtdYm1gBXEOpIV/8dDPiZyWkgrP4\\ncYgxOGnx7HD9x81UAuvfSICsMgD2htGRvmy4cVgJuBO/T+2LLI+4poU6q9AA2Qzttwgjmo\\nB733YNbL5wYZNYodeBjBikRQktuwi4IaJSDnqIDsh+29yWqsvS7SAohNOeHo8HWmXcFlNP\\nJMTDuCLXcTWrAjwubkImlyM1hcrBtJi5O1lnPFsrkB53kBZd0Luqf61ic+IrHnmuQgS+bN\\nQyMgsqP44Def6DljnIj1JePZgy5Xgs2Ew51ql+NzSvQPO7pzXrgPeRZPWpB/EB+ISgQs6R\\n4bIeFN2LP5fUOTZp8ga7RVgWNp9d2X7TQPzLPh7Ield3siVtKyBWNv1DOFwGMg+jBDpbxQ\\nEI8QuhG6n5KwuhUIB9yNsALSA6hJNo+/b3yCA3c6fKLVoyELAKV+eY/pCoqLGPGE12/bC1\\nrhHaUnfwDd4kPB8CHHsk7pWip+60wQAAAAMBAAEAAAGAXw+dHpY3o21lwP0v5h1VNVD+kX\\nmoVwNVfw0ToDKV8JzK+i0GA9xIA9VVAUlDCREtYmCXSbKyDVYgqRYQZ5d9aLTjGDIINZtl\\nSeUWtaJVZQF7cvAYq4g5fmxR2vIE+zC9+Jl7e5PlGJg1okKLXpMO6fVoy/AxlVkaoJVq6q\\nxLwQ3WKbeZIrgjHPYIx1N9oy5fbbwJ9oq2jIE8YabXlkfonhcwEN6UhtIlj8dy1apruXGT\\nVDfzHMRrDfrzt0TrdUqmqgo/istP89sggtkJ8uuPtkBFHTjao8MiBsshy1iDVbIno9gDbJ\\nJgYyunmSgEjEZpp09+mkgwfZO3/RDLRPF1SRAGBNy27CH8/bh9gAVRhAPi0GLclNi292Ya\\nNrGvjMcRlYAsWL3mZ9aTbv0j7Qi8qdWth+rZ+tBmNToUVVl5iLxifgo0kjiXAehZB1LaQV\\nyuMXlXOGmt9V2/DPACA9getQJQONxrLAcgHdjMiuwD8r7d+m/kE4+cOTakOlzrfrwBAAAA\\nwQCVTQTvuyBW3JemMPtRLifQqdwMGRPokm5nTn+JSJQvg+dNpL7hC0k3IesKs63gxuuHoq\\n4q1xkMmCMvihT8oVlxrezEjsO/QMCxe6Sr9eMfHAjrdPeHsPaf9oOgG9vEEH9dEilHpnlb\\n97Vyl9EHm1iahONM1gWdXkPjIfnQzYPvSLZPtBBSI0XBjCTifMnCRgd3s2bdm7kh+7XA+C\\nrX62WfPIJKL+OhMIf+ED4HBJTd/vU34Vk73yvqHzqel0ZQnRoAAADBAOGSm6TNBptV7S5P\\nwT3BhGYSm35/7nCFTilyfy5/8EUmifUFittRIvgDoXBWeZEwvqIiQ55iX9mYmNmb0KbPCw\\ncqN/BtXWItAvyTDZ6PeI2m2aUj+rW2R3ZXEsBjgaNRtbPyMKQ69xtKRvHtNZNfgjpRQ4is\\nlbufhAK1YbUxrlfKaBGOcGyR7DNmUUUN6nptQbpOr1HQc5DOH17HIDnRPs44HIws3/apww\\nRBIjjy6GQNfJ/Ge8N4pxGoLl1qKO8xoQAAAMEA0Tat/E5mSsgjCgmFja/jOZJcrzZHwrPT\\n3NEbuAMQ/L3atKEINypmpJfjIAvNljKJwSUDMEWvs8qj8cSGCrtkcAv1YSm697TL2oC9HU\\nCFoOJAkH1X2CGTgHlR9it3j4aRJ3dXdL2k7aeoGXObfRWqBNPj0LOOZs64RA6scGAzo6MR\\n5WlcOxfV1wZuaM0fOd+PBmIlFEE7Uf6AY/UahBAxaFV2+twgK9GCDcu1t4Ye9wZ9kZ4Nal\\n0fkKD4uN4DRO8hAAAAFm10dWhhaUBrYnAxLWxocC1hMTQ1MzMBAgME\\n-----END OPENSSH PRIVATE KEY-----";
  private static final String CONFIG =
      "{\"ssl\":true,\"host\":\"fakehost.com\",\"port\":5432,\"schema\":\"public\",\"database\":\"postgres\",\"password\":\"<dummyPassword>\",\"username\":\"postgres\",\"tunnel_method\":{\"ssh_key\":\""
          + OPENSSH_PRIVATE_KEY
          + "\",\"tunnel_host\":\"faketunnel.com\",\"tunnel_port\":22,\"tunnel_user\":\"ec2-user\",\"tunnel_method\":\"SSH_KEY_AUTH\"}}";

  @Test
  public void getKeyPair() throws Exception {
    JsonNode config = (new ObjectMapper()).readTree(CONFIG);
    // We do not want to open session to ssh host, so using constructor instead of getInstance()
    SshTunnel sshTunnel = new SshTunnel(
        config,
        Arrays.asList(new String[] {"host"}),
        Arrays.asList(new String[] {"port"}),
        TunnelMethod.SSH_KEY_AUTH,
        "faketunnel.com",
        22,
        "tunnelUser",
        OPENSSH_PRIVATE_KEY,
        "tunnelUserPassword",
        "fakeHost.com",
        5432);
    KeyPair authKeyPair = sshTunnel.getPrivateKeyPair();
    assertNotNull(authKeyPair);// actually, all is good if there is no exception on previous line
  }
  /**
   * This test verifies that 'net.i2p.crypto:eddsa' is present and EdDSA is supported. If
   * net.i2p.crypto:eddsa will be removed from project, then will be thrown: generator not correctly
   * initialized
   *
   * @throws Exception
   */
  @Test
  public void edDsaIsSupported() throws Exception {
    var keygen = SecurityUtils.getKeyPairGenerator("EdDSA");
    final String message = "hello world";
    KeyPair keyPair = keygen.generateKeyPair();

    byte[] signedMessage = sign(keyPair.getPrivate(), message);

    assertTrue(new EdDSASecurityProviderRegistrar().isSupported());
    assertTrue(verify(keyPair.getPublic(), signedMessage, message));
  }

  private byte[] sign(final PrivateKey privateKey, final String message) throws Exception {
    var signature = SecurityUtils.getSignature("NONEwithEdDSA");
    signature.initSign(privateKey);

    signature.update(message.getBytes(StandardCharsets.UTF_8));

    return signature.sign();
  }

  private boolean verify(final PublicKey publicKey, byte[] signed, final String message)
      throws Exception {
    var signature = SecurityUtils.getSignature("NONEwithEdDSA");
    signature.initVerify(publicKey);

    signature.update(message.getBytes(StandardCharsets.UTF_8));

    return signature.verify(signed);
  }

}
