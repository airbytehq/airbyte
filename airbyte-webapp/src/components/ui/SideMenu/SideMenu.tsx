import React from "react";
import styled from "styled-components";

import { MenuItem } from "./MenuItem";

export interface SideMenuItem {
  path: string;
  name: string | React.ReactNode;
  indicatorCount?: number;
  component?: React.ComponentType;
  id?: string;
  /**
   * Will be called instead of the onSelect of the component if this link is clicked.
   */
  onClick?: () => void;
}

export interface CategoryItem {
  category?: string | React.ReactNode;
  routes: SideMenuItem[];
}

interface SideMenuProps {
  data: CategoryItem[];
  activeItem?: string;
  onSelect: (id: string) => void;
}

const Content = styled.nav`
  min-width: 155px;
`;

const Category = styled.div`
  margin-bottom: 30px;
`;

const CategoryName = styled.div`
  padding: 5px 8px;
  font-weight: 500;
  font-size: 10px;
  line-height: 12px;
  opacity: 0.5;
  text-transform: uppercase;
`;

export const SideMenu: React.FC<SideMenuProps> = ({ data, onSelect, activeItem }) => {
  return (
    <Content>
      {data.map((categoryItem, index) => (
        <Category key={index}>
          {categoryItem.category && <CategoryName>{categoryItem.category}</CategoryName>}
          {categoryItem.routes.map((route) => (
            <MenuItem
              id={route.id}
              key={route.path}
              name={route.name}
              isActive={activeItem?.endsWith(route.path)}
              count={route.indicatorCount}
              onClick={route.onClick ?? (() => onSelect(route.path))}
            />
          ))}
        </Category>
      ))}
    </Content>
  );
};
