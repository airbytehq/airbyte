import React from "react";
import styled from "styled-components";

interface IProps {
  name: string | React.ReactNode;
  isActive?: boolean;
  id?: string;
  onClick: () => void;
}

const Item = styled.div<{ isActive?: boolean }>`
  padding: 10px 0;
  cursor: pointer;
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  line-height: 15px;
  color: ${({ theme, isActive }) => (isActive ? theme.primaryColor : "#999999")};
  border-bottom: 2px solid ${({ theme, isActive }) => (isActive ? theme.primaryColor : "transparent")};
  margin-bottom: -1px;
  margin-right: 60px;
  &:nth-child(4) {
    margin-right: 0px;
  }
`;

const TabItem: React.FC<IProps> = ({ isActive, name, id, onClick }) => {
  return (
    <Item data-testid={id} isActive={isActive} onClick={onClick}>
      {name}
    </Item>
  );
};

export default TabItem;
