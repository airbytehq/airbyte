import { Menu } from "@headlessui/react";
import classNames from "classnames";
import React from "react";

import { Button } from "../Button";
import { Text } from "../Text";
import styles from "./DropdownMenu.module.scss";

export interface DropdownMenuItemType {
  label: string;
  value: string;
  primary?: boolean;
  img?: React.ReactNode;
}

export const DropdownMenu: React.FC<
  React.PropsWithChildren<{
    label: React.ReactNode;
    options: DropdownMenuItemType[];
    onChange: (item: DropdownMenuItemType) => void;
    disabled: boolean;
  }>
> = ({ options, label, disabled, onChange }) => {
  return (
    <Menu className={styles.dropDownMenu} as="div">
      <Menu.Button as={React.Fragment}>
        <Button disabled={disabled}>{label}</Button>
      </Menu.Button>
      <Menu.Items className={styles.items}>
        {options?.map((item, index) => (
          <Menu.Item key={index}>
            {({ active }) => (
              <button
                className={classNames(styles.item, { [styles.active]: active, [styles.primary]: item.primary })}
                title={item.label}
                onClick={() => onChange(item)}
              >
                <Text className={styles.text} size="lg">
                  {item.label}
                </Text>
                {item.img}
              </button>
            )}
          </Menu.Item>
        ))}
      </Menu.Items>
    </Menu>
  );
};
