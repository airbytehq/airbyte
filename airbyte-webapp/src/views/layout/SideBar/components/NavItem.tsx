import classNames from "classnames";
import React from "react";
import { NavLink } from "react-router-dom";

import { FlexContainer } from "components/ui/Flex";
import { Text } from "components/ui/Text";

import styles from "./NavItem.module.scss";
import { useCalculateSidebarStyles } from "../GenericSideBar";
import { NotificationIndicator } from "../NotificationIndicator";

interface NavItemProps {
  label: React.ReactNode;
  icon: React.ReactNode;
  as: "a" | "button" | "navLink";
  to: string; // todo: make this not required for buttons
  className?: string;
  testId?: string;
  onClick?: () => void;
  withNotification?: boolean;
}

export const NavItem: React.FC<NavItemProps> = ({
  label,
  icon,
  to,
  testId,
  as,
  className,
  onClick,
  withNotification = false,
}) => {
  const navLinkClassName = useCalculateSidebarStyles();

  if (as === "a") {
    return (
      <a
        href={to}
        target="_blank"
        rel="noreferrer"
        className={classNames(styles.menuItem, className)}
        data-testid={testId}
      >
        <FlexContainer direction="column" alignItems="center" justifyContent="space-between">
          {icon}
          {withNotification && (
            <React.Suspense fallback={null}>
              <NotificationIndicator />
            </React.Suspense>
          )}
          <Text size="sm">{label}</Text>
        </FlexContainer>
      </a>
    );
  } else if (as === "navLink") {
    return (
      <NavLink className={classNames(navLinkClassName, className)} to={to} data-testid={testId}>
        <FlexContainer direction="column" alignItems="center" justifyContent="space-between">
          {icon}
          {withNotification && (
            <React.Suspense fallback={null}>
              <NotificationIndicator />
            </React.Suspense>
          )}
          <Text size="sm">{label}</Text>
        </FlexContainer>
      </NavLink>
    );
  } else if (as === "button") {
    return (
      <button className={classNames(styles.menuItem, className)} data-testid={testId} onClick={onClick}>
        <FlexContainer direction="column" alignItems="center" justifyContent="space-between">
          {icon}
          {withNotification && (
            <React.Suspense fallback={null}>
              <NotificationIndicator />
            </React.Suspense>
          )}
          <Text size="sm">{label}</Text>
        </FlexContainer>
      </button>
    );
  }
  return null;
};
