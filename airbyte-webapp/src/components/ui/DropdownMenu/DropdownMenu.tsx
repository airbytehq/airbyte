import { autoUpdate, useFloating, offset } from "@floating-ui/react-dom";
import { Menu } from "@headlessui/react";
import classNames from "classnames";
import React from "react";

import { Text } from "components/ui/Text";

import styles from "./DropdownMenu.module.scss";
import { DropdownMenuProps, DropdownMenuItemType, IconPositionType, MenuItemContentProps } from "./types";

const MenuItemContent: React.FC<React.PropsWithChildren<MenuItemContentProps>> = ({ data }) => {
  return (
    <>
      {((data?.icon && data?.iconPosition === IconPositionType.LEFT) || !data?.iconPosition) && (
        <span className={classNames(styles.icon, styles.positionLeft)}>{data.icon}</span>
      )}
      <Text className={styles.text} size="lg">
        {data.displayName}
      </Text>
      {data?.icon && data?.iconPosition === IconPositionType.RIGHT && (
        <span className={classNames(styles.icon, styles.positionRight)}>{data.icon}</span>
      )}
    </>
  );
};

export const DropdownMenu: React.FC<React.PropsWithChildren<DropdownMenuProps>> = ({
  options,
  children,
  onChange,
  placement = "bottom",
  displacement = 5,
}) => {
  const { x, y, reference, floating, strategy } = useFloating({
    middleware: [offset(displacement)],
    whileElementsMounted: autoUpdate,
    placement,
  });

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
                {({ active }) =>
                  item.type === DropdownMenuItemType.LINK ? (
                    <a
                      className={classNames(styles.item, item?.className, {
                        [styles.active]: active,
                      })}
                      target="_blank"
                      rel="noreferrer"
                      href={item?.href}
                      title={item.displayName}
                      data-id={item.displayName}
                    >
                      <MenuItemContent data={item} />
                    </a>
                  ) : (
                    <button
                      className={classNames(styles.item, item?.className, {
                        [styles.active]: active,
                      })}
                      data-id={item.displayName}
                      title={item.displayName}
                      onClick={() => onChange && onChange(item)}
                    >
                      <MenuItemContent data={item} />
                    </button>
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
