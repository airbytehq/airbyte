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

package io.airbyte.integrations.base.ssh;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;

public class SshHelpers {

  public static ConnectorSpecification getSpecAndInjectSsh() throws IOException {
    final ConnectorSpecification originalSpec = Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
    return injectSshIntoSpec(originalSpec);
  }

  public static ConnectorSpecification injectSshIntoSpec(final ConnectorSpecification connectorSpecification) throws IOException {
    final ConnectorSpecification originalSpec = Jsons.clone(connectorSpecification);
    final ObjectNode propNode = (ObjectNode) originalSpec.getConnectionSpecification().get("properties");
    propNode.set("tunnel_method", Jsons.deserialize(MoreResources.readResource("ssh-tunnel-spec.json")));
    return originalSpec;
  }

}
