import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBook, faCog } from "@fortawesome/free-solid-svg-icons";
import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { FormattedMessage } from "react-intl";
import { NavLink } from "react-router-dom";

import { Routes } from "pages/routes";
import config from "config";

import useConnector from "components/hooks/services/useConnector";
import { Link } from "components";
import Indicator from "components/Indicator";

import Source from "views/layout/SideBar/components/SourceIcon";
import Connections from "views/layout/SideBar/components/ConnectionsIcon";
import Destination from "views/layout/SideBar/components/DestinationIcon";
import { WorkspacePopout } from "packages/cloud/views/workspaces/WorkspacePopout";

const Bar = styled.nav`
  width: 100px;
  min-width: 65px;
  height: 100%;
  background: ${({ theme }) => theme.darkPrimaryColor};
  padding: 23px 3px 15px 4px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`;

const Menu = styled.ul`
  padding: 0;
  margin: 20px 0 0;
  width: 100%;
`;

const MenuItem = styled(NavLink)`
  color: ${({ theme }) => theme.greyColor30};
  width: 100%;
  cursor: pointer;
  border-radius: 4px;
  height: 70px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-weight: normal;
  font-size: 12px;
  line-height: 15px;
  margin-top: 7px;
  text-decoration: none;
  position: relative;

  &.active {
    color: ${({ theme }) => theme.whiteColor};
    background: ${({ theme }) => theme.primaryColor};
  }
`;

const MenuLinkItem = styled.a`
  color: ${({ theme }) => theme.greyColor30};
  width: 100%;
  cursor: pointer;
  height: 70px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-weight: normal;
  font-size: 12px;
  line-height: 15px;
  margin-top: 7px;
  text-decoration: none;
`;

const Text = styled.div`
  margin-top: 7px;
`;

const DocsIcon = styled(FontAwesomeIcon)`
  font-size: 18px;
  line-height: 18px;
`;

const HelpIcon = styled(FontAwesomeIcon)`
  font-size: 21px;
  line-height: 21px;
`;

const SettingsIcon = styled(FontAwesomeIcon)`
  font-size: 16px;
  line-height: 15px;
`;

const Notification = styled(Indicator)`
  position: absolute;
  top: 11px;
  right: 23px;
`;

const WorkspaceButton = styled.div`
  font-size: 9px;
  line-height: 21px;
  height: 21px;
  //display: flex;
  //justify-content: center;
  //align-items: center;
  color: ${({ theme }) => theme.whiteColor};
  border-radius: 10px;
  margin-top: 13px;
  background: rgba(255, 255, 255, 0.2);
  cursor: pointer;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 3px;
  text-align: center;
`;

const SideBar: React.FC = () => {
  const { hasNewVersions } = useConnector();

  return (
    <Bar>
      <div>
        <Link to={Routes.Root}>
          <img src="/simpleLogo.svg" alt="logo" height={33} width={33} />
        </Link>
        <WorkspacePopout>
          {({ onOpen, value }) => (
            <WorkspaceButton onClick={onOpen}>{value}</WorkspaceButton>
          )}
        </WorkspacePopout>
        <Menu>
          <li>
            <MenuItem to={Routes.Connections} activeClassName="active">
              <Connections />
              <Text>
                <FormattedMessage id="sidebar.connections" />
              </Text>
            </MenuItem>
          </li>
          <li>
            <MenuItem
              to={Routes.Root}
              exact
              activeClassName="active"
              isActive={(_, location) =>
                location.pathname === Routes.Root ||
                location.pathname.startsWith(Routes.Source)
              }
            >
              <Source />
              <Text>
                <FormattedMessage id="sidebar.sources" />
              </Text>
            </MenuItem>
          </li>
          <li>
            <MenuItem to={Routes.Destination} activeClassName="active">
              <Destination />
              <Text>
                <FormattedMessage id="sidebar.destinations" />
              </Text>
            </MenuItem>
          </li>
        </Menu>
      </div>
      <Menu>
        <li>
          <MenuLinkItem href={config.ui.slackLink} target="_blank">
            {/*@ts-ignore slack icon fails here*/}
            <HelpIcon icon={faSlack} />
            <Text>
              <FormattedMessage id="sidebar.slack" />
            </Text>
          </MenuLinkItem>
        </li>
        <li>
          <MenuLinkItem href={config.ui.docsLink} target="_blank">
            <DocsIcon icon={faBook} />
            <Text>
              <FormattedMessage id="sidebar.docs" />
            </Text>
          </MenuLinkItem>
        </li>
        <li>
          <MenuItem
            to={`${Routes.Settings}${Routes.Account}`}
            activeClassName="active"
            isActive={(_, location) =>
              location.pathname.startsWith(Routes.Settings)
            }
          >
            {hasNewVersions ? <Notification /> : null}
            <SettingsIcon icon={faCog} />
            <Text>
              <FormattedMessage id="sidebar.settings" />
            </Text>
          </MenuItem>
        </li>
      </Menu>
    </Bar>
  );
};

export default SideBar;
