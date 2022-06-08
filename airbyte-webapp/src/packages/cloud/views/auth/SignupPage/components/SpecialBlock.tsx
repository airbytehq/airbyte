import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

const Arrow = styled(FontAwesomeIcon)`
  font-size: 16px;
  display: block;
  margin-left: 7px;
  color: ${({ theme }) => theme.redColor};
`;

const ArrowMiddle = styled(Arrow)`
  font-size: 12px;
  margin: 4px 10px -2px 22px;
`;

const ArrowBottom = styled(Arrow)`
  font-size: 9px;
  margin-left: 10px;
`;

const HighlightBlock = styled.span<{ red?: boolean }>`
  color: ${({ theme, red }) => (red ? theme.redColor : "inhered")};
  font-family: ${({ theme }) => theme.italicFont};
`;

const SpecialOffer = styled.div`
  margin-top: 27px;
  background: ${({ theme }) => theme.redTransparentColor};
  border-radius: 12px;
  padding: 14px 8px 14px 12px;
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const SumBlock = styled.span`
  display: inline-block;
  background: ${({ theme }) => theme.lightRedColor};
  border: 4px solid ${({ theme }) => theme.redColor};
  box-sizing: border-box;
  box-shadow: 0 2px 4px ${({ theme }) => theme.cardShadowColor};
  border-radius: 8px;
  font-family: ${({ theme }) => theme.italicFont};
  padding: 0 5px;
`;

const SpecialBlock: React.FC = () => {
  return (
    <SpecialOffer>
      <div>
        <Arrow icon={faArrowRight} />
        <ArrowMiddle icon={faArrowRight} />
        <ArrowBottom icon={faArrowRight} />
      </div>
      <div>
        <FormattedMessage
          id="login.activateAccess.subtitle"
          values={{
            sum: (sum: React.ReactNode) => <SumBlock>{sum}</SumBlock>,
            special: (special: React.ReactNode) => <HighlightBlock red>{special}</HighlightBlock>,
            free: (free: React.ReactNode) => <HighlightBlock>{free}</HighlightBlock>,
          }}
        />
      </div>
    </SpecialOffer>
  );
};

export default SpecialBlock;
