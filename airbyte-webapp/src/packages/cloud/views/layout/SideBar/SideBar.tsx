import { faQuestionCircle } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { NavLink } from "react-router-dom";
import styled from "styled-components";

import { Link } from "components";
import { CreditsIcon } from "components/icons/CreditsIcon";

import { FeatureItem, IfFeatureEnabled } from "hooks/services/Feature";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { useIntercom } from "packages/cloud/services/thirdParty/intercom";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/WorkspacesService";
import { WorkspacePopout } from "packages/cloud/views/workspaces/WorkspacePopout";
import ChatIcon from "views/layout/SideBar/components/ChatIcon";
import ConnectionsIcon from "views/layout/SideBar/components/ConnectionsIcon";
import DestinationIcon from "views/layout/SideBar/components/DestinationIcon";
import DocsIcon from "views/layout/SideBar/components/DocsIcon";
import OnboardingIcon from "views/layout/SideBar/components/OnboardingIcon";
import SettingsIcon from "views/layout/SideBar/components/SettingsIcon";
import SidebarPopout, { Icon, Item } from "views/layout/SideBar/components/SidebarPopout";
import SourceIcon from "views/layout/SideBar/components/SourceIcon";
import { NotificationIndicator } from "views/layout/SideBar/NotificationIndicator";
import { useCalculateSidebarStyles, getPopoutStyles } from "views/layout/SideBar/SideBar";

import { RoutePaths } from "../../../../../pages/routePaths";

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
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);
  const { show } = useIntercom();
  const handleChatUs = () => show();

  const navLinkClassName = useCalculateSidebarStyles();

  return (
    <Bar>
      <div>
        <Link to={workspace.displaySetupWizard ? RoutePaths.Onboarding : RoutePaths.Connections}>
          <img src="/simpleLogo.svg" alt="logo" height={33} width={33} />
        </Link>
        <WorkspacePopout>
          {({ onOpen, value }) => <WorkspaceButton onClick={onOpen}>{value}</WorkspaceButton>}
        </WorkspacePopout>
        <Menu>
          {workspace.displaySetupWizard ? (
            <li>
              <NavLink className={navLinkClassName} to={RoutePaths.Onboarding}>
                <OnboardingIcon />
                <Text>
                  <FormattedMessage id="sidebar.onboarding" />
                </Text>
              </NavLink>
            </li>
          ) : null}
          <li>
            <NavLink className={navLinkClassName} to={RoutePaths.Connections}>
              <ConnectionsIcon />
              <Text>
                <FormattedMessage id="sidebar.connections" />
              </Text>
            </NavLink>
          </li>
          <li>
            <NavLink className={navLinkClassName} to={RoutePaths.Source}>
              <SourceIcon />
              <Text>
                <FormattedMessage id="sidebar.sources" />
              </Text>
            </NavLink>
          </li>
          <li>
            <NavLink className={navLinkClassName} to={RoutePaths.Destination}>
              <DestinationIcon />
              <Text>
                <FormattedMessage id="sidebar.destinations" />
              </Text>
            </NavLink>
          </li>
        </Menu>
      </div>
      <Menu>
        <li>
          <NavLink className={navLinkClassName} to={CloudRoutes.Credits}>
            <CreditsIcon />
            <Text>
              <FormattedNumber value={cloudWorkspace.remainingCredits} />
            </Text>
          </NavLink>
        </li>
        <li>
          <SidebarPopout options={[{ value: "docs" }, { value: "slack" }, { value: "status" }, { value: "recipes" }]}>
            {({ onOpen, isOpen }) => (
              <button className={getPopoutStyles(isOpen)} onClick={onOpen} tabIndex={0}>
                <DocsIcon />
                <Text>
                  <FormattedMessage id="sidebar.resources" />
                </Text>
              </button>
            )}
          </SidebarPopout>
        </li>
        <li>
          <SidebarPopout
            options={[
              { value: "ticket" },
              {
                value: "chat",
                label: (
                  <Item onClick={handleChatUs}>
                    <Icon>
                      <ChatIcon />
                    </Icon>
                    <FormattedMessage id="sidebar.chat" />
                  </Item>
                ),
              },
            ]}
          >
            {({ onOpen, isOpen }) => (
              <button className={getPopoutStyles(isOpen)} onClick={onOpen} role="menu" tabIndex={0}>
                <FontAwesomeIcon icon={faQuestionCircle} size="2x" />
                <Text>
                  <FormattedMessage id="sidebar.support" />
                </Text>
              </button>
            )}
          </SidebarPopout>
        </li>
        <li>
          <NavLink className={navLinkClassName} to={RoutePaths.Settings}>
            <IfFeatureEnabled feature={FeatureItem.AllowUpdateConnectors}>
              <React.Suspense fallback={null}>
                <NotificationIndicator />
              </React.Suspense>
            </IfFeatureEnabled>
            <SettingsIcon />
            <Text>
              <FormattedMessage id="sidebar.settings" />
            </Text>
          </NavLink>
        </li>
      </Menu>
    </Bar>
  );
};

export default SideBar;
