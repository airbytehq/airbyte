import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import { Separator } from "components/Separator";

import { Mailto } from "./Mailto";

const Container = styled.div`
  width: 100%;
  height: auto;
`;

const Heading = styled.div`
  font-style: normal;
  font-weight: 600;
  font-size: 24px;
  color: ${({ theme }) => theme.black300};
`;

const Message = styled.div`
  font-weight: 400;
  font-size: 12px;
  line-height: 20px;
  color: #6b6b6f;
  margin-bottom: 2px;
`;

const EnterpriseCell: React.FC = () => {
  const { formatMessage } = useIntl();
  return (
    <Container>
      <Heading>
        <FormattedMessage id="feature.cell.enterprise.customPrising" />
      </Heading>
      <Separator />
      <Message>
        <FormattedMessage id="feature.cell.enterprise.message" />
      </Message>
      <Separator />
      <Mailto
        email={formatMessage({ id: "daspire.support.mail" })}
        subject={formatMessage({ id: "feature.cell.enterprise.btnText" })}
        body={formatMessage({ id: "feature.cell.enterprise.mailBody" })}
      >
        <Button full size="lg">
          <FormattedMessage id="feature.cell.enterprise.btnText" />
        </Button>
      </Mailto>
    </Container>
  );
};

export default EnterpriseCell;
