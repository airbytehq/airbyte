import React from "react";
import styled from "styled-components";

interface StepItemProps {
  active?: boolean;
  current?: boolean;
  children?: React.ReactNode;
}

const Content = styled.div<{ active?: boolean }>`
  display: flex;
  flex-direction: row;
  align-items: center;

  &:last-child > .next-path {
    display: none;
  }

  &:first-child > .previous-path {
    display: none;
  }
`;

const Item = styled.div<{ active?: boolean }>`
  height: 46px;
  width: 46px;
  border-radius: 50%;
  padding: 6px 5px;
  border: 1px solid ${({ theme, active }) => (active ? theme.primaryColor : theme.lightTextColor)};
  background: ${({ theme, active }) => (active ? theme.primaryColor : theme.transparentColor)};
  color: ${({ theme, active }) => (active ? theme.whiteColor : theme.lightTextColor)};
  font-weight: normal;
  font-size: 18px;
  line-height: 22px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: 0.8s;
`;

const Path = styled.div<{ active?: boolean }>`
  width: 25px;
  height: 1px;
  background: ${({ theme }) => theme.lightTextColor};

  &:before {
    content: "";
    display: block;
    width: ${({ active }) => (active ? 25 : 0)}px;
    height: 1px;
    background: ${({ theme }) => theme.primaryColor};
    transition: 0.8s 0.5s;
  }

  &:first-child:before {
    transition: 0.8s;
  }
`;

const StepItem: React.FC<StepItemProps> = ({ active, children }) => {
  return (
    <Content>
      <Path active={active} className="previous-path" />
      <Item active={active}>{children}</Item>
      <Path active={active} className="next-path" />
    </Content>
  );
};

export default StepItem;
