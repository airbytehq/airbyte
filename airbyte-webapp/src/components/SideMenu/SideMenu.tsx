import React from "react";
import styled from "styled-components";

import MenuItem from "./components/MenuItem";

export type SideMenuItem = {
  id: string;
  name: string | React.ReactNode;
  indicatorCount?: number;
};

type SideMenuProps = {
  data: SideMenuItem[];
  activeItem?: string;
  onSelect: (id: string) => void;
};

const Content = styled.nav`
  min-width: 147px;
`;

const SideMenu: React.FC<SideMenuProps> = ({ data, onSelect, activeItem }) => {
  return (
    <Content>
      {data.map((item) => (
        <MenuItem
          key={item.id}
          name={item.name}
          isActive={item.id === activeItem}
          count={item.indicatorCount}
          onClick={() => onSelect(item.id)}
        />
      ))}
    </Content>
  );
};

export default SideMenu;
