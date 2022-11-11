import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { faRocket } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { NavLink, useLocation } from "react-router-dom";

import { Link } from "components";
import { Version } from "components/common/Version";
import { Text } from "components/ui/Text";

import { useConfig } from "config";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { links } from "utils/links";

import { DocsIcon } from "../../../components/icons/DocsIcon";
import { DropdownMenu } from "../../../components/ui/DropdownMenu";
import { RoutePaths } from "../../../pages/routePaths";
import { ReactComponent as AirbyteLogo } from "./airbyteLogo.svg";
import ConnectionsIcon from "./components/ConnectionsIcon";
import DestinationIcon from "./components/DestinationIcon";
import OnboardingIcon from "./components/OnboardingIcon";
import RecipesIcon from "./components/RecipesIcon";
import SettingsIcon from "./components/SettingsIcon";
import SourceIcon from "./components/SourceIcon";
import { NotificationIndicator } from "./NotificationIndicator";
import styles from "./SideBar.module.scss";

export const useCalculateSidebarStyles = () => {
  const location = useLocation();

  const menuItemStyle = (isActive: boolean) => {
    const isChild = location.pathname.split("/").length > 4 && location.pathname.split("/")[3] !== "settings";
    return classNames(styles.menuItem, { [styles.active]: isActive, [styles.activeChild]: isChild && isActive });
  };

  return ({ isActive }: { isActive: boolean }) => menuItemStyle(isActive);
};

const SideBar: React.FC = () => {
  const config = useConfig();
  const workspace = useCurrentWorkspace();
  const navLinkClassName = useCalculateSidebarStyles();
  const { formatMessage } = useIntl();

  return (
    <nav className={styles.nav}>
      <div>
        <Link
          to={workspace.displaySetupWizard ? RoutePaths.Onboarding : RoutePaths.Connections}
          aria-label={formatMessage({ id: "sidebar.homepage" })}
        >
          <AirbyteLogo height={33} width={33} />
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
          <DropdownMenu
            placement="right"
            displacement={10}
            options={[
              {
                as: "a",
                href: links.docsLink,
                icon: <DocsIcon />,
                displayName: formatMessage({ id: "sidebar.documentation" }),
              },
              {
                as: "a",
                href: links.slackLink,
                icon: <FontAwesomeIcon icon={faSlack} />,
                displayName: formatMessage({ id: "sidebar.joinSlack" }),
              },
              {
                as: "a",
                href: links.tutorialLink,
                icon: <RecipesIcon />,
                displayName: formatMessage({ id: "sidebar.recipes" }),
              },
            ]}
          >
            {({ open }) => (
              <button className={classNames(styles.dropdownMenuButton, { [styles.open]: open })}>
                <DocsIcon />
                <Text className={styles.text} size="sm">
                  <FormattedMessage id="sidebar.resources" />
                </Text>
              </button>
            )}
          </DropdownMenu>
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
