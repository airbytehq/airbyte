import React from "react";
import styled from "styled-components";

import MenuItem from "./components/MenuItem";

export type SideMenuItem = {
  id: string;
  name: string | React.ReactNode;
  indicatorCount?: number;
};

export type CategoryItem = {
  category?: string | React.ReactNode;
  routes: SideMenuItem[];
};

type SideMenuProps = {
  data: CategoryItem[];
  activeItem?: string;
  onSelect: (id: string) => void;
};

const Content = styled.nav`
  min-width: 147px;
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

const SideMenu: React.FC<SideMenuProps> = ({ data, onSelect, activeItem }) => {
  return (
    <Content>
      {data.map((categoryItem) => (
        <Category>
          {categoryItem.category ? (
            <CategoryName>{categoryItem.category}</CategoryName>
          ) : null}
          {categoryItem.routes.map((item) => (
            <MenuItem
              key={item.id}
              name={item.name}
              isActive={item.id === activeItem}
              count={item.indicatorCount}
              onClick={() => onSelect(item.id)}
            />
          ))}
        </Category>
      ))}
    </Content>
  );
};

export default SideMenu;
