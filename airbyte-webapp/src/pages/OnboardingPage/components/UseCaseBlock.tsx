import React from "react";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import { FormattedMessage } from "react-intl";

type UseCaseBlockProps = {
  count: number;
  id: string;
  onSkip: (id: string) => void;
};

const Block = styled(ContentCard)`
  margin-bottom: 10px;
  width: 100%;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  flex-direction: row;
  align-items: center;
  font-size: 16px;
  line-height: 28px;
`;

const Num = styled.div`
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: ${({ theme }) => theme.primaryColor};
  color: ${({ theme }) => theme.whiteColor};
  margin-right: 13px;
  font-weight: bold;
  font-size: 12px;
  line-height: 28px;
  display: inline-block;
  text-align: center;
`;

const SkipButton = styled.div`
  color: ${({ theme }) => theme.lightTextColor};
  font-size: 16px;
  line-height: 28px;
  cursor: pointer;
`;

const UseCaseBlock: React.FC<UseCaseBlockProps> = ({ id, count, onSkip }) => {
  return (
    <Block>
      <div>
        <Num>{count}</Num>
        <FormattedMessage id={`onboarding.${id}`} />
      </div>
      <SkipButton onClick={() => onSkip(id)}>
        <FormattedMessage id="onboarding.skip" />
      </SkipButton>
    </Block>
  );
};

export default UseCaseBlock;
