import React from "react";
import styled from "styled-components";

interface IProps {
  name: string | React.ReactNode;
  isActive?: boolean;
  count?: number;
  id?: string;
  onClick: () => void;
}

const Item = styled.div<{
  isActive?: boolean;
}>`
  width: 100%;
  padding: 6px 8px 7px;
  border-radius: 4px;
  cursor: pointer;
  background: ${({ theme, isActive }) => (isActive ? theme.primaryColor12 : "none")};
  font-style: normal;
  font-weight: ${({ isActive }) => (isActive ? "bold" : "500")};
  font-size: 12px;
  line-height: 15px;
  color: ${({ theme, isActive }) => (isActive ? theme.primaryColor : theme.greyColor60)};
`;

const Counter = styled.div`
  min-width: 12px;
  height: 12px;
  padding: 0 3px;
  text-align: center;
  border-radius: 15px;
  background: ${({ theme }) => theme.dangerColor};
  font-size: 8px;
  line-height: 13px;
  color: ${({ theme }) => theme.whiteColor};
  display: inline-block;
  margin-left: 5px;
`;

export const MenuItem: React.FC<IProps> = ({ count, isActive, name, id, onClick }) => {
  return (
    <Item data-testid={id} isActive={isActive} onClick={onClick}>
      {name}
      {count ? <Counter>{count}</Counter> : null}
    </Item>
  );
};
