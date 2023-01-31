import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { faRocket } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { NavLink, useLocation } from "react-router-dom";

import { Link } from "components";
import { Version } from "components/common/Version";
import { DocsIcon } from "components/icons/DocsIcon";
import { DropdownMenu } from "components/ui/DropdownMenu";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { Text } from "components/ui/Text";

import { useConfig } from "config";
import { useExperiment } from "hooks/services/Experiment";
import { links } from "utils/links";

import { ReactComponent as AirbyteLogo } from "./airbyteLogo.svg";
import RecipesIcon from "./components/RecipesIcon";
import SettingsIcon from "./components/SettingsIcon";
import { MainNav } from "./MainNav";
import { NotificationIndicator } from "./NotificationIndicator";
import styles from "./SideBar.module.scss";
import { RoutePaths } from "../../../pages/routePaths";

export const useCalculateSidebarStyles = () => {
  const location = useLocation();

  const menuItemStyle = (isActive: boolean) => {
    const isChild = location.pathname.split("/").length > 4 && location.pathname.split("/")[3] !== "settings";
    return classNames(styles.menuItem, { [styles.active]: isActive, [styles.activeChild]: isChild && isActive });
  };

  return ({ isActive }: { isActive: boolean }) => menuItemStyle(isActive);
};

interface SideBarProps {
  additionalTopItems?: JSX.Element;
  bottomMenuItems?: JSX.Element[];
}

export const SideBar: React.FC<SideBarProps> = ({ additionalTopItems, bottomMenuItems }) => {
  const config = useConfig();
  const navLinkClassName = useCalculateSidebarStyles();
  const { formatMessage } = useIntl();

  const OSSBottomMenuItems = [
    <a href={links.updateLink} target="_blank" rel="noreferrer" className={styles.menuItem} data-testid="updateLink">
      <FontAwesomeIcon className={styles.helpIcon} icon={faRocket} />
      <Text className={styles.text} size="sm">
        <FormattedMessage id="sidebar.update" />
      </Text>
    </a>,
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
    </DropdownMenu>,
    <NavLink className={navLinkClassName} to={RoutePaths.Settings}>
      <React.Suspense fallback={null}>
        <NotificationIndicator />
      </React.Suspense>
      <SettingsIcon />
      <Text className={styles.text} size="sm">
        <FormattedMessage id="sidebar.settings" />
      </Text>
    </NavLink>,
  ];

  if (config.version) {
    OSSBottomMenuItems.push(<Version primary />);
  }

  const bottomMenuArray = bottomMenuItems ?? OSSBottomMenuItems;

  return (
    <FlexContainer direction="column" alignItems="center" justifyContent="space-between" className={styles.menuContent}>
      <nav className={styles.nav}>
        <FlexItem>
          <div>
            <Link to={RoutePaths.Connections} aria-label={formatMessage({ id: "sidebar.homepage" })}>
              <AirbyteLogo height={33} width={33} />
            </Link>
            {additionalTopItems}
          </div>
        </FlexItem>
        <FlexContainer
          direction="column"
          alignItems="center"
          justifyContent="space-between"
          className={styles.menuContent}
        >
          <FlexItem>
            <MainNav />
          </FlexItem>
          <FlexItem className={styles.bottomMenu}>
            <ul className={styles.menu} data-testid="navBottomMenu">
              {bottomMenuArray.map((item, idx) => {
                // todo: better key
                return <li key={idx}>{item}</li>;
              })}
            </ul>
          </FlexItem>
        </FlexContainer>
      </nav>
    </FlexContainer>
  );
};
