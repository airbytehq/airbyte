import React from "react";
import { FormattedMessage } from "react-intl";

import { Callout } from "components/ui/Callout";
import { FlexContainer } from "components/ui/Flex";
import { StatusIcon } from "components/ui/StatusIcon";
import { Text } from "components/ui/Text";

const ErrorSection: React.FC<{
  errorTitle: React.ReactNode;
  errorMessage: React.ReactNode;
}> = ({ errorMessage, errorTitle }) => (
  <Callout variant="error">
    <FlexContainer alignItems="flex-start" gap="sm">
      <StatusIcon />
      <FlexContainer direction="column">
        <Text size="lg">{errorTitle}</Text>
        <Text>{errorMessage}</Text>
      </FlexContainer>
    </FlexContainer>
  </Callout>
);

const TestingConnectionError: React.FC<{ errorMessage: React.ReactNode }> = ({ errorMessage }) => (
  <ErrorSection errorTitle={<FormattedMessage id="form.failedTests" />} errorMessage={errorMessage} />
);

const FetchingConnectorError: React.FC = () => (
  <ErrorSection
    errorTitle={<FormattedMessage id="form.failedFetchingConnector" />}
    errorMessage={<FormattedMessage id="form.tryAgain" />}
  />
);

export { TestingConnectionError, FetchingConnectorError };
