import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { faRocket } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";
import { NavLink, useLocation } from "react-router-dom";

import { Link } from "components";
import { Text } from "components/ui/Text";
import Version from "components/Version";

import { useConfig } from "config";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { links } from "utils/links";

import { RoutePaths } from "../../../pages/routePaths";
import ConnectionsIcon from "./components/ConnectionsIcon";
import DestinationIcon from "./components/DestinationIcon";
import DocsIcon from "./components/DocsIcon";
import OnboardingIcon from "./components/OnboardingIcon";
import RecipesIcon from "./components/RecipesIcon";
import SettingsIcon from "./components/SettingsIcon";
import { SidebarDropdownMenu, SidebarDropdownMenuItemType } from "./components/SidebarDropdownMenu";
import SourceIcon from "./components/SourceIcon";
import { NotificationIndicator } from "./NotificationIndicator";
import styles from "./SideBar.module.scss";

export const useCalculateSidebarStyles = () => {
  const location = useLocation();

  const menuItemStyle = (isActive: boolean) => {
    const isChild = location.pathname.split("/").length > 4 && location.pathname.split("/")[3] !== "settings";
    return classnames(styles.menuItem, { [styles.active]: isActive, [styles.activeChild]: isChild && isActive });
  };

  return ({ isActive }: { isActive: boolean }) => menuItemStyle(isActive);
};

const SideBar: React.FC = () => {
  const config = useConfig();
  const workspace = useCurrentWorkspace();
  const navLinkClassName = useCalculateSidebarStyles();

  return (
    <nav className={styles.nav}>
      <div>
        <Link to={workspace.displaySetupWizard ? RoutePaths.Onboarding : RoutePaths.Connections}>
          <img src="/simpleLogo.svg" alt="logo" height={33} width={33} />
        </Link>
        <ul className={styles.menu}>
          {workspace.displaySetupWizard ? (
            <li>
              <NavLink className={navLinkClassName} to={RoutePaths.Onboarding}>
                <OnboardingIcon />
                <Text className={styles.text} size="sm">
                  <FormattedMessage id="sidebar.onboarding" />
                </Text>
              </NavLink>
            </li>
          ) : null}
          <li>
            <NavLink className={navLinkClassName} to={RoutePaths.Connections}>
              <ConnectionsIcon />
              <Text className={styles.text} size="sm">
                <FormattedMessage id="sidebar.connections" />
              </Text>
            </NavLink>
          </li>
          <li>
            <NavLink className={navLinkClassName} to={RoutePaths.Source}>
              <SourceIcon />
              <Text className={styles.text} size="sm">
                <FormattedMessage id="sidebar.sources" />
              </Text>
            </NavLink>
          </li>
          <li>
            <NavLink className={navLinkClassName} to={RoutePaths.Destination}>
              <DestinationIcon />
              <Text className={styles.text} size="sm">
                <FormattedMessage id="sidebar.destinations" />
              </Text>
            </NavLink>
          </li>
        </ul>
      </div>
      <ul className={styles.menu}>
        <li>
          <a href={links.updateLink} target="_blank" rel="noreferrer" className={styles.menuItem}>
            <FontAwesomeIcon className={styles.helpIcon} icon={faRocket} />
            <Text className={styles.text} size="sm">
              <FormattedMessage id="sidebar.update" />
            </Text>
          </a>
        </li>
        <li>
          <SidebarDropdownMenu
            label={{
              icon: <DocsIcon />,
              displayName: <FormattedMessage id="sidebar.resources" />,
            }}
            options={[
              {
                type: SidebarDropdownMenuItemType.LINK,
                href: links.docsLink,
                icon: <DocsIcon />,
                displayName: <FormattedMessage id="sidebar.documentation" />,
              },
              {
                type: SidebarDropdownMenuItemType.LINK,
                href: links.slackLink,
                icon: <FontAwesomeIcon icon={faSlack} />,
                displayName: <FormattedMessage id="sidebar.joinSlack" />,
              },
              {
                type: SidebarDropdownMenuItemType.LINK,
                href: links.recipesLink,
                icon: <RecipesIcon />,
                displayName: <FormattedMessage id="sidebar.recipes" />,
              },
            ]}
          />
        </li>
        <li>
          <NavLink className={navLinkClassName} to={RoutePaths.Settings}>
            <React.Suspense fallback={null}>
              <NotificationIndicator />
            </React.Suspense>
            <SettingsIcon />
            <Text className={styles.text} size="sm">
              <FormattedMessage id="sidebar.settings" />
            </Text>
          </NavLink>
        </li>
        {config.version ? (
          <li>
            <Version primary />
          </li>
        ) : null}
      </ul>
    </nav>
  );
};

export default SideBar;
