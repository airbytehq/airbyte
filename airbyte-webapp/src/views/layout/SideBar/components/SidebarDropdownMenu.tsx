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

interface LinkMenuItemProps {
  active: boolean;
  item: MenuItemLink;
}

const LinkMenuItem: React.FC<LinkMenuItemProps> = ({ active, item }) => {
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
};

interface ButtonMenuItemProps {
  active: boolean;
  item: MenuItemButton;
}

const ButtonMenuItem: React.FC<ButtonMenuItemProps> = ({ active, item }) => {
  return (
    <button className={classNames(styles.item, { [styles.active]: active })} onClick={item.onClick}>
      <span className={styles.icon}>{item.icon}</span>
      <Text size="lg">{item.displayName}</Text>
    </button>
  );
};

export const SidebarDropdownMenu: React.FC<{
  label: Label;
  options: Array<MenuItemLink | MenuItemButton>;
}> = ({ label, options }) => {
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
            {options.map((item, index) => (
              <Menu.Item key={index}>
                {({ active }) =>
                  item.type === SidebarDropdownMenuItemType.LINK ? (
                    <LinkMenuItem item={item} active={active} />
                  ) : (
                    <ButtonMenuItem item={item} active={active} />
                  )
                }
              </Menu.Item>
            ))}
          </Menu.Items>
        </>
      )}
    </Menu>
  );
};
