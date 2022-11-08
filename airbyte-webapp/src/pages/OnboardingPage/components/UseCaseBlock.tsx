import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Card } from "components/ui/Card";

interface UseCaseBlockProps {
  count: number;
  id: string;
  href: string;
  onSkip: (id: string) => void;
}

const Block = styled(Card)`
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

const SkipButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.lightTextColor};
  font-size: 16px;
  line-height: 28px;
  cursor: pointer;
  transition: color 0.3s;

  &:hover,
  &:focus-visible {
    color: ${({ theme }) => theme.blackColor};
  }
`;

const Link = styled.a`
  color: inherit;
  text-decoration: none;

  &:hover,
  &:focus-visible {
    text-decoration: underline;
  }
`;

const UseCaseBlock: React.FC<UseCaseBlockProps> = ({ id, count, onSkip, href }) => {
  return (
    <Block>
      <div>
        <Num>{count}</Num>
        <Link href={href} target="_blank">
          <FormattedMessage id={`onboarding.useCase.${id}`} />
        </Link>
      </div>
      <SkipButton onClick={() => onSkip(id)}>
        <FormattedMessage id="onboarding.skip" />
      </SkipButton>
    </Block>
  );
};

export default UseCaseBlock;
