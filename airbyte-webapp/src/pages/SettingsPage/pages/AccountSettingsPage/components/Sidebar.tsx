import * as React from "react";
import styled from "styled-components";
import { theme } from "theme";

import { GlobIcon } from "components/icons/GlobIcon";
import { LockIcon } from "components/icons/LockIcon";
import { UserIcon } from "components/icons/UserIcon";
import { SideMenuItem } from "components/TabMenu";

import useRouter from "hooks/useRouter";

import { AccountSettingsRoute } from "../AccountSettingsPage";

interface IProps {
  menuItems: SideMenuItem[];
  onSelectItem: (path: string) => void;
}

const SidebarContainer = styled.div`
  min-width: 300px;
  height: 490px;
  border-radius: 6px 0 0 6px;
  background: ${({ theme }) => theme.grey40};
  padding: 32px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const SidebarItem = styled.div`
  padding: 36px 0;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const ItemText = styled.div<{
  isSelected: boolean;
}>`
  cursor: pointer;
  font-style: normal;
  font-weight: 500;
  font-size: 14px;
  color: ${({ isSelected, theme }) => (isSelected ? theme.blue400 : "#6B6B6F")};
  margin-left: 12px;
`;

const SidebarItemIcon = (path: string, color: string) => {
  switch (path) {
    case AccountSettingsRoute.Account:
      return <UserIcon color={color} />;

    case AccountSettingsRoute.Language:
      return <GlobIcon color={color} />;

    case AccountSettingsRoute.Password:
      return <LockIcon color={color} />;

    default:
      return null;
  }
};

export const Sidebar: React.FC<IProps> = ({ menuItems, onSelectItem }) => {
  const { pathname } = useRouter();
  return (
    <SidebarContainer>
      {menuItems.map(({ name, path }) => (
        <SidebarItem onClick={() => onSelectItem(path)}>
          {SidebarItemIcon(path, pathname.split("/").at(-1) === path ? theme.blue400 : "#6B6B6F")}
          <ItemText isSelected={pathname.split("/").at(-1) === path}>{name}</ItemText>
        </SidebarItem>
      ))}
    </SidebarContainer>
  );
};
