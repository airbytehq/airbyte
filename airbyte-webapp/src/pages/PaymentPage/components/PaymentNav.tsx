import React from "react";
import styled from "styled-components";

import { RightArrowHeadIcon } from "components/icons/RightArrowHeadIcon";

export interface NavItem {
  path: string;
  name: string | React.ReactNode;
  component: React.ComponentType;
}

export interface NavMenuItem {
  category?: string | React.ReactNode;
  routes: NavItem[];
}

interface IProps {
  data: NavMenuItem[];
  activeItem?: string;
  onSelect: (id: string) => void;
}

const Navbar = styled.nav`
  width: 100%;
  height: 100px;
  background-color: ${({ theme }) => theme.white};
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const NavContent = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const ArrowIconContainer = styled.div`
  margin: 3px 60px 0 60px;
`;

const NavItem = styled.div<{ isActive?: boolean }>`
  font-weight: 400;
  font-size: 14px;
  color: ${({ theme, isActive }) => (isActive ? theme.primaryColor : "#6B6B6F")};
  cursor: pointer;
`;

const PaymentNav: React.FC<IProps> = ({ data, onSelect, activeItem }) => {
  return (
    <Navbar>
      {data.map((categoryItem, index) => (
        <NavContent key={index}>
          {categoryItem.routes.map((route, index) => (
            <>
              <NavItem isActive={activeItem?.endsWith(route.path)} onClick={() => onSelect(route.path)}>
                {route.name}
              </NavItem>
              {!(index + 1 >= categoryItem.routes.length) && (
                <ArrowIconContainer>
                  <RightArrowHeadIcon />
                </ArrowIconContainer>
              )}
            </>
          ))}
        </NavContent>
      ))}
    </Navbar>
  );
};

export default PaymentNav;
