import React from "react";
import styled from "styled-components";

const BreadcrumbsContainer = styled.div`
  font-weight: normal;
  cursor: default;
`;

const LastBreadcrumbsItem = styled.span`
  font-weight: bold;
`;

const BreadcrumbsItem = styled.div`
  display: inline-block;
  cursor: pointer;
  color: ${({ theme }) => theme.primaryColor};

  &:hover {
    opacity: 0.8;
  }
`;

export interface BreadcrumbsDataItem {
  name: string | React.ReactNode;
  onClick?: () => void;
}

interface BreadcrumbsProps {
  data: BreadcrumbsDataItem[];
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ data }) => {
  const lastIndex = data.length - 1;

  return (
    <BreadcrumbsContainer>
      {data.map((item, key) =>
        key === lastIndex ? (
          <LastBreadcrumbsItem key={`breadcrumbs-item-${key}`}>{item.name}</LastBreadcrumbsItem>
        ) : (
          <span key={`breadcrumbs-item-${key}`}>
            <BreadcrumbsItem onClick={item.onClick}>{item.name}</BreadcrumbsItem>
            <span> / </span>
          </span>
        )
      )}
    </BreadcrumbsContainer>
  );
};
