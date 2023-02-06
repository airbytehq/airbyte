import React from "react";
import { FormattedMessage } from "react-intl";

import { FlexContainer } from "components/ui/Flex";
import { StatusIcon } from "components/ui/StatusIcon";
import { Text } from "components/ui/Text";

const TestingConnectionSuccess: React.FC = () => (
  <FlexContainer data-id="success-result" justifyContent="center" gap="none">
    <StatusIcon status="success" />
    <Text size="lg">
      <FormattedMessage id="form.successTests" />
    </Text>
  </FlexContainer>
);

export default TestingConnectionSuccess;
