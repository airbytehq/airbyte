import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import { Separator } from "components/Separator";

const Container = styled.div`
  width: 100%;
  height: auto;
`;

const Heading = styled.div`
  ont-style: normal;
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
      <Button full size="lg">
        <FormattedMessage id="feature.cell.enterprise.btnText" />
      </Button>
    </Container>
  );
};

export default EnterpriseCell;
