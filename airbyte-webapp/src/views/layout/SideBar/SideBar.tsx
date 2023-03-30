import { faHome, faGear, faInbox, faDatabase } from "@fortawesome/free-solid-svg-icons";
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
import { useUser } from "core/AuthContext";
import useRouter from "hooks/useRouter";
import { LOCALES } from "locales";

import { RoutePaths } from "../../../pages/routePaths";
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
  margin-left: 10px;
  font-weight: 500;
  font-size: 15px;
`;

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

const DocumentationArrowIconContainer = styled.div`
  display: block;
  margin-left: 14px;
`;

export const useCalculateSidebarStyles = () => {
  const { location } = useRouter();

  const menuItemStyle = (isActive: boolean) => {
    const isChild = location.pathname.split("/").length > 2 && location.pathname.split("/")[1] !== "settings";
    return classnames(styles.menuItem, { [styles.active]: isActive, [styles.activeChild]: isChild && isActive });
  };

  return ({ isActive }: { isActive: boolean }) => menuItemStyle(isActive);
};

export const useCalculateSidebarItemStyles = (route: string) => {
  const { location } = useRouter();
  const menuItemStyle = () => {
    const isActive = location.pathname.split("/").length >= 2 && location.pathname.split("/")[1] === route;
    return classnames(styles.menuItem, { [styles.inActive]: !isActive }, { [styles.active]: isActive });
  };

  return menuItemStyle();
};

export const getPopoutStyles = (isOpen?: boolean) => {
  return classnames(styles.menuItem, { [styles.popoutOpen]: isOpen });
};

const SideBar: React.FC = () => {
  const { user } = useUser();
  const docsLink = user.lang === LOCALES.ENGLISH ? links.docsLink : `${links.docsLink}/${user.lang}/`;
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
        </Menu>
      </div>
      <Menu>
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
        <a
          href={docsLink}
          target="_blank"
          rel="noreferrer"
          className={useCalculateSidebarItemStyles(RoutePaths.Documentation)}
        >
          <DocumentationIcon width={16} height={16} />
          <Text>
            <FormattedMessage id="sidebar.documentation" />
          </Text>
          <DocumentationArrowIconContainer>
            <DocumentationArrowIcon height={11} width={11} />
          </DocumentationArrowIconContainer>
        </a>
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
