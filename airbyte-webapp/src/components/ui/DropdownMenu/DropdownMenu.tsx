import { autoUpdate, Placement, useFloating, offset } from "@floating-ui/react-dom";
import { Menu } from "@headlessui/react";
import classNames from "classnames";
import React from "react";

import { Text } from "components/ui/Text";

import styles from "./DropdownMenu.module.scss";

export enum DropdownMenuItemType {
  LINK = "link",
  BUTTON = "button",
}

export enum IconPositionType {
  LEFT = "left",
  RIGHT = "right",
}

interface MenuItemLink {
  type: DropdownMenuItemType.LINK;
  href: string;
  icon?: React.ReactNode;
  displayName: React.ReactNode | string;
  iconPosition?: IconPositionType;
}

interface MenuItemButton {
  type: DropdownMenuItemType.BUTTON;
  // icon?: React.ReactNode;
  icon?: any;
  displayName: React.ReactNode | string;
  iconPosition?: IconPositionType;
  primary?: boolean;
  onSelect?: (item: MenuItemLink | MenuItemButton) => void;
}

// interface MenuItem {
//   data: MenuItemLink | MenuItemButton;
// }
//
// const MenuItem: React.FC<React.PropsWithChildren<MenuItem>> = ({ data }) => {
//   return (
//     <>
//       {((data?.icon && data?.iconPosition === IconPositionType.LEFT) || !data?.iconPosition) && (
//         <span className={classNames(styles.icon, styles.positionLeft)}>{data.icon}</span>
//       )}
//       <Text className={styles.text} size="lg">
//         {data.displayName}
//       </Text>
//       {data?.icon && data?.iconPosition === IconPositionType.RIGHT && (
//         <span className={classNames(styles.icon, styles.positionRight)}>{data.icon}</span>
//       )}
//     </>
//   );
// };

interface DropdownMenu {
  options: Array<MenuItemLink | MenuItemButton>;
  children: ({ open }: { open: boolean }) => React.ReactNode;
  placement?: Placement;
  displacement?: number;
}

export const DropdownMenu: React.FC<React.PropsWithChildren<DropdownMenu>> = ({
  options,
  children,
  placement = "bottom",
  displacement = 5,
}) => {
  const { x, y, reference, floating, strategy } = useFloating({
    middleware: [offset(displacement)],
    whileElementsMounted: autoUpdate,
    placement,
  });

  // const menuItem = (item: MenuItemLink | MenuItemButton) => {
  //   return (
  //     <>
  //       {((item?.icon && item?.iconPosition === IconPositionType.LEFT) || !item?.iconPosition) && (
  //         <span className={classNames(styles.icon, styles.positionLeft)}>{item.icon}</span>
  //       )}
  //       <Text className={styles.text} size="lg">
  //         {item.displayName}
  //       </Text>
  //       {item?.icon && item?.iconPosition === IconPositionType.RIGHT && (
  //         <span className={classNames(styles.icon, styles.positionRight)}>{item.icon}</span>
  //       )}
  //     </>
  //   );
  // };

  return (
    <Menu ref={reference} className={styles.dropdownMenu} as="div">
      {({ open }) => (
        <>
          <Menu.Button as={React.Fragment}>{children({ open })}</Menu.Button>
          <Menu.Items
            ref={floating}
            className={styles.items}
            style={{
              position: strategy,
              top: y ?? 0,
              left: x ?? 0,
            }}
          >
            {options.map((item, index) => (
              <Menu.Item key={index}>
                {({ active }) => (
                  <>
                    {item.type === DropdownMenuItemType.LINK && (
                      <a
                        className={classNames(styles.item, { [styles.active]: active })}
                        href={item.href}
                        target="_blank"
                        rel="noreferrer"
                        data-id={item.displayName}
                      >
                        {((item?.icon && item?.iconPosition === IconPositionType.LEFT) || !item?.iconPosition) && (
                          <span className={classNames(styles.icon, styles.positionLeft)}>{item.icon}</span>
                        )}
                        <Text className={styles.text} size="lg">
                          {item.displayName}
                        </Text>
                        {item?.icon && item?.iconPosition === IconPositionType.RIGHT && (
                          <span className={classNames(styles.icon, styles.positionRight)}>{item.icon}</span>
                        )}
                        {/* <MenuItem data={item} /> */}
                      </a>
                    )}
                    {item.type === DropdownMenuItemType.BUTTON && (
                      <button
                        className={classNames(styles.item, {
                          [styles.active]: active,
                          [styles.primary]: item?.primary,
                        })}
                        onClick={() => {
                          if (item?.onSelect) {
                            item.onSelect(item);
                          }
                        }}
                        data-id={item.displayName}
                      >
                        {((item?.icon && item?.iconPosition === IconPositionType.LEFT) || !item?.iconPosition) && (
                          <span className={classNames(styles.icon, styles.positionLeft)}>{item.icon}</span>
                        )}
                        <Text className={styles.text} size="lg">
                          {item.displayName}
                        </Text>
                        {item?.icon && item?.iconPosition === IconPositionType.RIGHT && (
                          <span className={classNames(styles.icon, styles.positionRight)}>{item.icon}</span>
                        )}
                        {/* <MenuItem data={item} /> */}
                      </button>
                    )}
                  </>
                )}
              </Menu.Item>
            ))}
          </Menu.Items>
        </>
      )}
    </Menu>
  );
};
