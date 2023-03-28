import { faHome, faGear, faInbox, faDatabase } from "@fortawesome/free-solid-svg-icons";
// import { faGear } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";
import { NavLink } from "react-router-dom";
import styled from "styled-components";

import { Link } from "components";
import { DocumentationArrowIcon } from "components/icons/DocumentationArrowIcon";
import { DocumentationIcon } from "components/icons/DocumentationIcon";

import { links } from "config/links";
// import Version from "components/Version";
// import { useConfig } from "config";
// import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useUser } from "core/AuthContext";
import useRouter from "hooks/useRouter";

import { RoutePaths } from "../../../pages/routePaths";
// import ConnectionsIcon from "./components/ConnectionsIcon";
// import DestinationIcon from "./components/DestinationIcon";
// import DocsIcon from "./components/DocsIcon";
// import OnboardingIcon from "./components/OnboardingIcon";
// import SettingsIcon from "./components/SettingsIcon";
// import SidebarPopout from "./components/SidebarPopout";
// import SourceIcon from "./components/SourceIcon";
// import { NotificationIndicator } from "./NotificationIndicator";
import styles from "./SideBar.module.scss";

const Menu = styled.ul`
  padding: 0;
  margin: 20px 0 0 0;
  width: 100%;
`;

const MenuItem = styled.li`
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Text = styled.div`
  // margin-top: 2px;
  margin-left: 10px;
  font-weight: 500;
  font-size: 15px;
`;

// const TextSetting = styled.div`
//   color: black;
//   padding-left: 15px;
//   font-weight: bold;
// `;

const LogoContainer = styled.div`
  margin-top: 30px;
  margin-bottom: 50px;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  font-weight: normal;
  width: 100%;
  height: 60px;
`;

const Logo = styled.img`
  max-width: 130px;
  height: auto;
`;

const MenuItemIcon = styled(FontAwesomeIcon)`
  font-size: 16px;
  line-height: 16px;
  font-weight: normal;
`;

const UserDetail = styled.div`
  font-weight: 500;
  font-size: 12px;
  line-height: 15px;
  color: #aaaaaa;
  margin-top: 40px;
`;

// const DocumentationItem = styled.div`
//   padding-left: 54px;
//   height: 50px;
//   display: flex;
//   flex-direction: row;
//   align-items: center;
//   margin-top: 7px;

//   &:hover {
//     background: #eae9ff;
//     color: #4f46e5;
//     cursor: pointer;
//     transition: all $transition ease-out;
//   }
// `;

const DocumentationArrowIconContainer = styled.div`
  display: block;
  margin-left: 16px;
`;

export const useCalculateSidebarStyles = () => {
  const { location } = useRouter();

  const menuItemStyle = (isActive: boolean) => {
    // const isChild = location.pathname.split("/").length > 4 && location.pathname.split("/")[3] !== "settings";
    const isChild = location.pathname.split("/").length > 2 && location.pathname.split("/")[1] !== "settings";
    return classnames(styles.menuItem, { [styles.active]: isActive, [styles.activeChild]: isChild && isActive });
  };

  return ({ isActive }: { isActive: boolean }) => menuItemStyle(isActive);
};

export const useCalculateSidebarItemStyles = (route: string) => {
  const { location } = useRouter();
  const menuItemStyle = () => {
    // const isActive = location.pathname.split("/").length >= 4 && location.pathname.split("/")[3] === route;
    const isActive = location.pathname.split("/").length >= 2 && location.pathname.split("/")[1] === route;
    // const isSetting = route === "settings";
    return classnames(
      styles.menuItem,
      { [styles.inActive]: !isActive },
      // { [styles.inActiveSetting]: isSetting },
      { [styles.active]: isActive }
    );
  };

  return menuItemStyle();
};

export const getPopoutStyles = (isOpen?: boolean) => {
  return classnames(styles.menuItem, { [styles.popoutOpen]: isOpen });
};

// const toDocsPage = () =>{
//  window.location.href = links.docsLink
// }

const SideBar: React.FC = () => {
  // const config = useConfig();
  // const workspace = useCurrentWorkspace();
  const { user } = useUser();
  return (
    <div className={styles.sidebar}>
      <div>
        <Link to="" $clear>
          <LogoContainer>
            <Logo src="/daspireLogo1.svg" alt="logo" />
          </LogoContainer>
        </Link>
        <Menu>
          <MenuItem>
            <NavLink className={useCalculateSidebarItemStyles(RoutePaths.Connections)} to={RoutePaths.Connections}>
              <div>
                <MenuItemIcon icon={faHome} />
              </div>
              <Text>
                <FormattedMessage id="sidebar.DaspireDashboard" />
              </Text>
            </NavLink>
          </MenuItem>
          <MenuItem>
            <NavLink className={useCalculateSidebarItemStyles(RoutePaths.Source)} to={RoutePaths.Source}>
              <div>
                <MenuItemIcon icon={faInbox} />
              </div>
              <Text>
                <FormattedMessage id="sidebar.sources" />
              </Text>
            </NavLink>
          </MenuItem>
          <MenuItem>
            <NavLink className={useCalculateSidebarItemStyles(RoutePaths.Destination)} to={RoutePaths.Destination}>
              <div>
                <MenuItemIcon icon={faDatabase} />
              </div>
              <Text>
                <FormattedMessage id="sidebar.destinations" />
              </Text>
            </NavLink>
          </MenuItem>
          {/* {workspace.displaySetupWizard ? (*/}
          {/*  <li>*/}
          {/*    <NavLink className={navLinkClassName} to={RoutePaths.Onboarding}>*/}
          {/*      <OnboardingIcon />*/}
          {/*      <Text>*/}
          {/*        <FormattedMessage id="sidebar.onboarding" />*/}
          {/*      </Text>*/}
          {/*    </NavLink>*/}
          {/*  </li>*/}
          {/* ) : null}*/}
          {/* <li>*/}
          {/*  <NavLink className={navLinkClassName} to={RoutePaths.Connections}>*/}
          {/*    <ConnectionsIcon />*/}
          {/*    <Text>*/}
          {/*      <FormattedMessage id="sidebar.connections" />*/}
          {/*    </Text>*/}
          {/*  </NavLink>*/}
          {/* </li>*/}
          {/* <li>*/}
          {/*  <NavLink className={navLinkClassName} to={RoutePaths.Source}>*/}
          {/*    <SourceIcon />*/}
          {/*    <Text>*/}
          {/*      <FormattedMessage id="sidebar.sources" />*/}
          {/*    </Text>*/}
          {/*  </NavLink>*/}
          {/* </li>*/}
          {/* <li>*/}
          {/*  <NavLink className={navLinkClassName} to={RoutePaths.Destination}>*/}
          {/*    <DestinationIcon />*/}
          {/*    <Text>*/}
          {/*      <FormattedMessage id="sidebar.destinations" />*/}
          {/*    </Text>*/}
          {/*  </NavLink>*/}
          {/* </li>*/}
        </Menu>
      </div>
      <Menu>
        {/* <li>*/}
        {/*  <a href={config.links.updateLink} target="_blank" rel="noreferrer" className={styles.menuItem}>*/}
        {/*    <MenuItemIcon icon={faRocket} />*/}
        {/*    <Text>*/}
        {/*      <FormattedMessage id="sidebar.update" />*/}
        {/*    </Text>*/}
        {/*  </a>*/}
        {/* </li>*/}
        {/* <li>*/}
        {/*  <SidebarPopout options={[{ value: "docs" }, { value: "slack" }, { value: "recipes" }]}>*/}
        {/*    {({ onOpen, isOpen }) => (*/}
        {/*      <button className={getPopoutStyles(isOpen)} onClick={onOpen}>*/}
        {/*        <DocsIcon />*/}
        {/*        <Text>*/}
        {/*          <FormattedMessage id="sidebar.resources" />*/}
        {/*        </Text>*/}
        {/*      </button>*/}
        {/*    )}*/}
        {/*  </SidebarPopout>*/}
        {/* </li>*/}

        {/* <li>*/}
        {/*  <NavLink className={navLinkClassName} to={RoutePaths.Settings}>*/}
        {/*    <React.Suspense fallback={null}>*/}
        {/*      <NotificationIndicator />*/}
        {/*    </React.Suspense>*/}
        {/*    <SettingsIcon />*/}
        {/*    <Text>*/}
        {/*      <FormattedMessage id="sidebar.settings" />*/}
        {/*    </Text>*/}
        {/*  </NavLink>*/}
        {/* </li>*/}
        <MenuItem>
          <NavLink className={useCalculateSidebarItemStyles(RoutePaths.Settings)} to={RoutePaths.Settings}>
            <div>
              <MenuItemIcon icon={faGear} />
            </div>
            <Text>
              <FormattedMessage id="sidebar.DaspireSetting" />
            </Text>
          </NavLink>
        </MenuItem>
        <NavLink
          to={links.docsLink}
          target="_blank"
          className={useCalculateSidebarItemStyles(RoutePaths.Documentation)}
        >
          <DocumentationIcon width={16} height={16} />
          <Text>
            <FormattedMessage id="sidebar.documentation" />
          </Text>
          <DocumentationArrowIconContainer>
            <DocumentationArrowIcon height={10} width={10} />
          </DocumentationArrowIconContainer>
        </NavLink>
        {/* <li>
          <ButtonCenter>
            <Button>
              <SettingIcon icon={faGear} />
              <TextSetting>
                <FormattedMessage id="sidebar.DaspireSetting" />
              </TextSetting>
            </Button>
          </ButtonCenter>
        </li>
        {config.version ? (
          <li>
            <Version primary />
          </li>
        ) : null} */}
        <UserDetail>
          {`${user.firstName} ${user.lastName}`}
          <br />
          {`(${user.account})`}
        </UserDetail>
      </Menu>
    </div>
  );
};

export default SideBar;
