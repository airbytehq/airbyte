import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import { Separator } from "components/Separator";

interface IProps {
  price?: number;
  onSelectPlan?: () => void;
}

const Container = styled.div`
  width: 100%;
  height: auto;
`;

const PricingContainer = styled.div`
  width: 100%;
  display: flex;
`;

const Price = styled.div`
  font-style: normal;
  font-weight: 800;
  font-size: 24px;
  color: ${({ theme }) => theme.black300};
`;

const PerMonthText = styled.div`
  font-style: normal;
  font-weight: 500;
  font-size: 12px;
  line-height: 24px;
  color: #6b6b6f;
`;

const Message = styled.div`
  font-weight: 400;
  font-size: 12px;
  line-height: 20px;
  color: #6b6b6f;
`;

const ProcessionalCell: React.FC<IProps> = ({ price = 0, onSelectPlan }) => {
  return (
    <Container>
      <PricingContainer>
        <Price>${price}</Price>&nbsp;<PerMonthText>/mo</PerMonthText>
      </PricingContainer>
      <Separator />
      <Message>
        <FormattedMessage id="feature.cell.processional.message" />
      </Message>
      <Separator />
      <Button full size="lg" onClick={onSelectPlan}>
        <FormattedMessage id="feature.cell.processional.btnText" />
      </Button>
    </Container>
  );
};

export default ProcessionalCell;
