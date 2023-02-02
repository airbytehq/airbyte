import classNames from "classnames";
import React from "react";
import { NavLink, useLocation } from "react-router-dom";

import { FlexContainer } from "components/ui/Flex";
import { Text } from "components/ui/Text";

import styles from "./NavItem.module.scss";
import { NotificationIndicator } from "../NotificationIndicator";

interface NavItemProps extends NavItemInnerProps {
  as: "a" | "div" | "navLink";
  to: string; // todo: make this not required for buttons
  className?: string;
  testId?: string;
}

interface NavItemInnerProps {
  label: React.ReactNode;
  icon: React.ReactNode;
  withNotification?: boolean;
}

const NavItemInner: React.FC<NavItemInnerProps> = ({ icon, label, withNotification }) => {
  return (
    <FlexContainer direction="column" alignItems="center" justifyContent="center" className={styles.fullHeight}>
      {icon}
      {withNotification && (
        <React.Suspense fallback={null}>
          <NotificationIndicator />
        </React.Suspense>
      )}
      <Text size="sm">{label}</Text>
    </FlexContainer>
  );
};
export const useCalculateSidebarStyles = (className?: string) => {
  const location = useLocation();

  const menuItemStyle = (isActive?: boolean) => {
    const isChild = location.pathname.split("/").length > 4 && location.pathname.split("/")[3] !== "settings";

    return classNames(styles.menuItem, className, {
      [styles.active]: isActive,
      [styles.activeChild]: isChild && isActive,
    });
  };

  return ({ isActive }: { isActive: boolean }) => menuItemStyle(isActive);
};
export const NavItem: React.FC<NavItemProps> = ({
  label,
  icon,
  to,
  testId,
  as,
  className,
  withNotification = false,
}) => {
  const navLinkClassName = useCalculateSidebarStyles(className);

  if (as === "a") {
    return (
      <a
        href={to}
        target="_blank"
        rel="noreferrer"
        className={classNames(styles.menuItem, className)}
        data-testid={testId}
      >
        <NavItemInner label={label} icon={icon} withNotification={withNotification} />
      </a>
    );
  } else if (as === "navLink") {
    return (
      <NavLink className={navLinkClassName} to={to} data-testid={testId}>
        <NavItemInner label={label} icon={icon} withNotification={withNotification} />
      </NavLink>
    );
  }
  return null;
};
