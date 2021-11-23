import React from "react";
import styled from "styled-components";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { NavLink } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faStar } from "@fortawesome/free-solid-svg-icons";

import { Routes } from "packages/cloud/routes";
import { useConfig } from "config";

import useWorkspace from "hooks/services/useWorkspace";
import { Link } from "components";
import { WorkspacePopout } from "packages/cloud/views/workspaces/WorkspacePopout";

import ConnectionsIcon from "views/layout/SideBar/components/ConnectionsIcon";
import DestinationIcon from "views/layout/SideBar/components/DestinationIcon";
import DocsIcon from "views/layout/SideBar/components/DocsIcon";
import OnboardingIcon from "views/layout/SideBar/components/OnboardingIcon";
import SettingsIcon from "views/layout/SideBar/components/SettingsIcon";
import SourceIcon from "views/layout/SideBar/components/SourceIcon";
import { useGetWorkspace } from "packages/cloud/services/workspaces/WorkspacesService";
import { NotificationIndicator } from "views/layout/SideBar/NotificationIndicator";

const CreditsIcon = styled(FontAwesomeIcon)`
  font-size: 21px;
  line-height: 21px;
`;

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
  position: relative;
  z-index: 9999;
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

const WorkspaceButton = styled.div`
  font-size: 9px;
  line-height: 21px;
  font-weight: 400;
  height: 21px;
  color: ${({ theme }) => theme.whiteColor};
  border-radius: 10px;
  margin-top: 13px;
  background: rgba(255, 255, 255, 0.2);
  cursor: pointer;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 8px;
  text-align: center;
`;

const SideBar: React.FC = () => {
  const config = useConfig();
  const { workspace } = useWorkspace();
  const { data: cloudWorkspace } = useGetWorkspace(workspace.workspaceId);

  return (
    <Bar>
      <div>
        <Link
          to={
            workspace.displaySetupWizard
              ? Routes.Onboarding
              : Routes.Connections
          }
        >
          <img src="/simpleLogo.svg" alt="logo" height={33} width={33} />
        </Link>
        <WorkspacePopout>
          {({ onOpen, value }) => (
            <WorkspaceButton onClick={onOpen}>{value}</WorkspaceButton>
          )}
        </WorkspacePopout>
        <Menu>
          {workspace.displaySetupWizard ? (
            <li>
              <MenuItem to={Routes.Onboarding} activeClassName="active">
                <OnboardingIcon />
                <Text>
                  <FormattedMessage id="sidebar.onboarding" />
                </Text>
              </MenuItem>
            </li>
          ) : null}
          <li>
            <MenuItem to={Routes.Connections} activeClassName="active">
              <ConnectionsIcon />
              <Text>
                <FormattedMessage id="sidebar.connections" />
              </Text>
            </MenuItem>
          </li>
          <li>
            <MenuItem to={Routes.Source} activeClassName="active">
              <SourceIcon />
              <Text>
                <FormattedMessage id="sidebar.sources" />
              </Text>
            </MenuItem>
          </li>
          <li>
            <MenuItem to={Routes.Destination} activeClassName="active">
              <DestinationIcon />
              <Text>
                <FormattedMessage id="sidebar.destinations" />
              </Text>
            </MenuItem>
          </li>
        </Menu>
      </div>
      <Menu>
        <li>
          <MenuItem to={Routes.Credits} activeClassName="active">
            <CreditsIcon icon={faStar} />
            <Text>
              <FormattedMessage id="credits.credits" />
              <div>
                <FormattedNumber value={cloudWorkspace.remainingCredits} />
              </div>
            </Text>
          </MenuItem>
        </li>
        <li>
          <MenuLinkItem href={config.ui.docsLink} target="_blank">
            <DocsIcon />
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
            <React.Suspense fallback={null}>
              <NotificationIndicator />
            </React.Suspense>
            <SettingsIcon />
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
