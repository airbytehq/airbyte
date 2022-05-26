/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_BUCKET_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_CREDENTIALS;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.GCS;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

public class GcsErrorMessage extends ErrorMessage {

  {
    CONSTANTS.put("NoSuchKey", INCORRECT_BUCKET_NAME);
    CONSTANTS.put("NoSuchBucket", INCORRECT_BUCKET_NAME);
    CONSTANTS.put("SignatureDoesNotMatch", INCORRECT_CREDENTIALS);
  }

  @Override
  public ConnectorType getConnectorType() {
    return GCS;
  }

}
