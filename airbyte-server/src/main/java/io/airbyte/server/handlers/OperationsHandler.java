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

package io.airbyte.server.handlers;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.OperationCreate;
import io.airbyte.api.model.OperationIdRequestBody;
import io.airbyte.api.model.OperationRead;
import io.airbyte.api.model.OperationReadList;
import io.airbyte.api.model.OperationUpdate;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public class OperationsHandler {

  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidGenerator;

  @VisibleForTesting
  OperationsHandler(final ConfigRepository configRepository, final Supplier<UUID> uuidGenerator) {
    this.configRepository = configRepository;
    this.uuidGenerator = uuidGenerator;
  }

  public OperationsHandler(final ConfigRepository configRepository) {
    this(configRepository, UUID::randomUUID);
  }

  public OperationRead createOperation(OperationCreate operationCreate)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final UUID operationId = uuidGenerator.get();
    // TODO chris: to implement in next PR on custom-dbt-config
    return buildOperationRead(operationId);
  }

  public OperationRead updateOperation(OperationUpdate operationUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // TODO chris: to implement in next PR on custom-dbt-config
    return new OperationRead();
  }

  public OperationReadList listOperationsForConnection(ConnectionIdRequestBody connectionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final List<OperationRead> operationReads = Lists.newArrayList();
    // TODO chris: to implement in next PR on custom-dbt-config
    return new OperationReadList().operations(operationReads);
  }

  public OperationRead getOperation(OperationIdRequestBody operationIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildOperationRead(operationIdRequestBody.getOperationId());
  }

  public void deleteOperation(OperationIdRequestBody operationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final OperationRead OperationRead = getOperation(operationIdRequestBody);
    deleteOperation(OperationRead);
  }

  public void deleteOperation(OperationRead operationRead) throws ConfigNotFoundException, IOException, JsonValidationException {
    // TODO chris: to implement in next PR on custom-dbt-config
  }

  private OperationRead buildOperationRead(UUID operationId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // TODO chris: to implement in next PR on custom-dbt-config
    return new OperationRead();
  }

}
