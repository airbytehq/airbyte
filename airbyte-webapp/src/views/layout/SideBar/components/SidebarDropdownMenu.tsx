import { Menu } from "@headlessui/react";
import classNames from "classnames";
import React from "react";

import { Text } from "components/ui/Text";

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

interface Label {
  icon: React.ReactNode;
  displayName: React.ReactNode;
}

export const SidebarDropdownMenu: React.FC<{
  label: Label;
  options?: Array<MenuItemLink | MenuItemButton>;
}> = ({ label, options }) => {
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
            <span className={styles.icon}>{item.icon}</span>
            <Text size="lg">{item.displayName}</Text>
          </a>
        );
      case SidebarDropdownMenuItemType.BUTTON:
        return (
          <button className={classNames(styles.item, { [styles.active]: active })} onClick={item.onClick}>
            <span className={styles.icon}>{item.icon}</span>
            <Text size="lg">{item.displayName}</Text>
          </button>
        );
    }
  }

  return (
    <Menu className={styles.sidebarMenu} as="div">
      {({ open }) => (
        <>
          <Menu.Button className={classNames(styles.button, { [styles.open]: open })}>
            {label.icon}
            <Text className={styles.text} size="sm">
              {label.displayName}
            </Text>
          </Menu.Button>
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
