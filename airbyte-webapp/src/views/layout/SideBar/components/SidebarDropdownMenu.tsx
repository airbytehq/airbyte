import { Menu } from "@headlessui/react";
import classNames from "classnames";
import React from "react";

import styles from "./SidebarDropdownMenu.module.scss";

export enum SidebarDropdownMenuItemType {
  LINK = "link",
  BUTTON = "button",
}

interface MenuItemLink {
  type: SidebarDropdownMenuItemType.LINK;
  href: string;
  icon: React.ReactNode;
  displayName: React.ReactNode;
}

interface MenuItemButton {
  type: SidebarDropdownMenuItemType.BUTTON;
  icon: React.ReactNode;
  displayName: React.ReactNode;
  onClick: () => void;
}

export const SidebarDropdownMenu: React.FC<{
  children: React.ReactNode;
  options?: Array<MenuItemLink | MenuItemButton>;
}> = ({ children, options }) => {
  function menuItem(active: boolean, item: MenuItemLink | MenuItemButton): React.ReactNode {
    switch (item.type) {
      case SidebarDropdownMenuItemType.LINK:
        return (
          <a
            className={classNames(styles.item, { [styles.active]: active })}
            href={item.href}
            target="_blank"
            rel="noreferrer"
          >
            <span>{item.icon}</span>
            {item.displayName}
          </a>
        );
      case SidebarDropdownMenuItemType.BUTTON:
        return (
          <button className={classNames(styles.item, { [styles.active]: active })} onClick={item.onClick}>
            <span>{item.icon}</span>
            {item.displayName}
          </button>
        );
    }
  }

  return (
    <Menu className={styles.sidebarMenu} as="div">
      {({ open }) => (
        <>
          <Menu.Button className={classNames(styles.button, { [styles.open]: open })}>{children}</Menu.Button>
          <Menu.Items className={styles.items}>
            {options?.map((item, index) => (
              <Menu.Item key={index}>{({ active }) => menuItem(active, item)}</Menu.Item>
            ))}
          </Menu.Items>
        </>
      )}
    </Menu>
  );
};
