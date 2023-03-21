import React from "react";
import styled from "styled-components";

import { LeftArrowHeadIcon } from "components/icons/LeftArrowHeadIcon";

const BreadcrumbsContainer = styled.div`
  font-weight: normal;
  cursor: default;
  display: flex;
  align-items: center;
  height: 70px;
  font-size: 15px;
  flex-shrink: 0;
`;

const BreadcrumbsBlock = styled.div`
  display: flex;
  align-items: center;

  &:last-child {
    flex: 1;
  }
`;

const BreadcrumbsItem = styled.span<{ active: boolean }>`
  display: inline-block;
  cursor: ${({ active }) => (active ? "pointer" : "default")};
  color: ${({ theme, active }) => (active ? theme.primaryColor : "")};
  margin: 0 12px;
  flex: 1;
  word-break: break-all;

  &:hover {
    opacity: ${({ active }) => (active ? 0.8 : 1)};
  }
`;

const PaddingContainer = styled.span`
  padding: 0 12px;
  display: inline-block;
`;

interface IProps {
  data: Array<{ name: string | React.ReactNode; onClick?: () => void }>;
  currentStep: number;
}

const Breadcrumbs: React.FC<IProps> = ({ data, currentStep }) => {
  const lastIndex = data.length - 1;

  return (
    <BreadcrumbsContainer>
      {data.map((item, key) => (
        <BreadcrumbsBlock key={`breadcrumbs-item-${key}`}>
          {key === 0 && <LeftArrowHeadIcon />}
          <BreadcrumbsItem active={currentStep === key} onClick={item.onClick}>
            {item.name}
          </BreadcrumbsItem>
          {lastIndex !== key && <PaddingContainer> / </PaddingContainer>}
        </BreadcrumbsBlock>
      ))}
    </BreadcrumbsContainer>
  );
};

export default Breadcrumbs;
