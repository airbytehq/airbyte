import React from "react";
import styled from "styled-components";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { NavLink } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faStar } from "@fortawesome/free-regular-svg-icons";

import { useIntercom } from "packages/cloud/services/thirdParty/intercom";

import { CloudRoutes } from "packages/cloud/cloudRoutes";

import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { Link } from "components";
import { WorkspacePopout } from "packages/cloud/views/workspaces/WorkspacePopout";

import ConnectionsIcon from "views/layout/SideBar/components/ConnectionsIcon";
import DestinationIcon from "views/layout/SideBar/components/DestinationIcon";
import DocsIcon from "views/layout/SideBar/components/DocsIcon";
import OnboardingIcon from "views/layout/SideBar/components/OnboardingIcon";
import ChatIcon from "views/layout/SideBar/components/ChatIcon";
import SettingsIcon from "views/layout/SideBar/components/SettingsIcon";
import SourceIcon from "views/layout/SideBar/components/SourceIcon";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/WorkspacesService";
import { NotificationIndicator } from "views/layout/SideBar/NotificationIndicator";
import ResourcesPopup, {
  Icon,
  Item,
} from "views/layout/SideBar/components/ResourcesPopup";
import { RoutePaths } from "pages/routes";
import { FeatureItem, WithFeature } from "hooks/services/Feature";

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

  return (
    <Bar>
      <div>
        <Link
          to={
            workspace.displaySetupWizard
              ? RoutePaths.Onboarding
              : RoutePaths.Connections
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
              <MenuItem to={RoutePaths.Onboarding}>
                <OnboardingIcon />
                <Text>
                  <FormattedMessage id="sidebar.onboarding" />
                </Text>
              </MenuItem>
            </li>
          ) : null}
          <li>
            <MenuItem to={RoutePaths.Connections}>
              <ConnectionsIcon />
              <Text>
                <FormattedMessage id="sidebar.connections" />
              </Text>
            </MenuItem>
          </li>
          <li>
            <MenuItem to={RoutePaths.Source}>
              <SourceIcon />
              <Text>
                <FormattedMessage id="sidebar.sources" />
              </Text>
            </MenuItem>
          </li>
          <li>
            <MenuItem to={RoutePaths.Destination}>
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
          <MenuItem to={CloudRoutes.Credits}>
            <CreditsIcon icon={faStar} />
            <Text>
              <FormattedNumber value={cloudWorkspace.remainingCredits} />
            </Text>
          </MenuItem>
        </li>
        <li>
          <ResourcesPopup
            options={[
              { value: "docs" },
              { value: "slack" },
              { value: "status" },
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
              { value: "recipes" },
            ]}
          >
            {({ onOpen }) => (
              <MenuItem onClick={onOpen} as="div">
                <DocsIcon />
                <Text>
                  <FormattedMessage id="sidebar.resources" />
                </Text>
              </MenuItem>
            )}
          </ResourcesPopup>
        </li>
        <li>
          <MenuItem to={RoutePaths.Settings}>
            <WithFeature featureId={FeatureItem.AllowUpdateConnectors}>
              <React.Suspense fallback={null}>
                <NotificationIndicator />
              </React.Suspense>
            </WithFeature>
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
