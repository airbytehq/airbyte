import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import styled from "styled-components";

const Block = styled.div`
  background: ${({ theme }) => theme.darkBeigeColor};
  border-radius: 8px;
  padding: 18px 25px 22px;
  font-size: 13px;
  line-height: 20px;
  text-transform: uppercase;
`;
const Count = styled.div`
  padding-top: 6px;
  font-weight: bold;
  font-size: 24px;
  line-height: 29px;
`;

const RemainingCredits: React.FC = () => {
  return (
    <Block>
      <FormattedMessage id="credits.remainingCredits" />
      <Count>
        <FormattedNumber value={2200} />
      </Count>
    </Block>
  );
};

export default RemainingCredits;
