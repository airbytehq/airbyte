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

package io.airbyte.integrations.destination.template;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ConnectorSpecification;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DestinationTemplate implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(DestinationTemplate.class);

  // fixme - implement this method such that it returns the specification for the integration.
  // suggestion 1: save the jsonschema of the spec spec as a resource and just load it from disk.
  // the code in this method uses this suggestion. replace it if you'd like to take a different
  // approach.
  @Override
  public ConnectorSpecification spec() throws IOException {
    // return a jsonschema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  // fixme - implement this method such that it checks whether it can connect to the destination.
  // this should return a StandardCheckConnectionOutput with the status field set to true if the
  // connection succeeds and false if it does not. if false consider adding a message in the message
  // field to help the user figure out what they need to do differently so that the connection will
  // succeed.
  @Override
  public StandardCheckConnectionOutput check(JsonNode config) {
    // if(success) {
    // return new StandardCheckConnectionOutput().withStatus(Status.SUCCEEDED);
    // } else {
    // return new StandardCheckConnectionOutput().withStatus(Status.FAILED).withMessage("(optional) the
    // reason it failed");
    // }
    throw new RuntimeException("Not Implemented");
  }

  // fixme - implement this method such that it returns a consumer that can push messages to the
  // destination.
  @Override
  public DestinationConsumer<AirbyteMessage> write(JsonNode config, AirbyteCatalog catalog) throws IOException {
    return new RecordConsumer();
  }

  public static class RecordConsumer implements DestinationConsumer<AirbyteMessage> {

    @Override
    public void accept(AirbyteMessage message) throws Exception {
      // fixme - implement how to write a message to the destination
      throw new RuntimeException("Not Implemented");
    }

    @Override
    public void close() throws Exception {
      // fixme - implement hot to close the connection to the destination.
      throw new RuntimeException("Not Implemented");
    }

  }

  public static void main(String[] args) throws Exception {
    // fixme - instantiate your implementation of the Destination interface and pass it to
    // IntegrationRunner.
    final Destination destination = new DestinationTemplate();
    // this is airbyte's entrypoint into the integration. do not remove this line!
    LOGGER.info("starting destination: {}", DestinationTemplate.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", DestinationTemplate.class);
  }

}
