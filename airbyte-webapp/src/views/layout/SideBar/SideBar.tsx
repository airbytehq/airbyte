import { faRocket } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import { NavLink } from "react-router-dom";
import styled from "styled-components";

import { Link } from "components";
import Version from "components/Version";

import { useConfig } from "config";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

import { RoutePaths } from "../../../pages/routePaths";
import ConnectionsIcon from "./components/ConnectionsIcon";
import DestinationIcon from "./components/DestinationIcon";
import DocsIcon from "./components/DocsIcon";
import OnboardingIcon from "./components/OnboardingIcon";
import SettingsIcon from "./components/SettingsIcon";
import SidebarPopout from "./components/SidebarPopout";
import SourceIcon from "./components/SourceIcon";
import { NotificationIndicator } from "./NotificationIndicator";

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

const HelpIcon = styled(FontAwesomeIcon)`
  font-size: 21px;
  line-height: 21px;
`;

const SideBar: React.FC = () => {
  const config = useConfig();
  const workspace = useCurrentWorkspace();

  return (
    <Bar>
      <div>
        <Link to={workspace.displaySetupWizard ? RoutePaths.Onboarding : RoutePaths.Connections}>
          <img src="/simpleLogo.svg" alt="logo" height={33} width={33} />
        </Link>
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
          <MenuLinkItem href={config.links.updateLink} target="_blank">
            <HelpIcon icon={faRocket} />
            <Text>
              <FormattedMessage id="sidebar.update" />
            </Text>
          </MenuLinkItem>
        </li>
        <li>
          <SidebarPopout options={[{ value: "docs" }, { value: "slack" }, { value: "recipes" }]}>
            {({ onOpen }) => (
              <MenuItem onClick={onOpen} as="div">
                <DocsIcon />
                <Text>
                  <FormattedMessage id="sidebar.resources" />
                </Text>
              </MenuItem>
            )}
          </SidebarPopout>
        </li>

        <li>
          <MenuItem
            to={RoutePaths.Settings}
            // isActive={(_, location) =>
            //   location.pathname.startsWith(RoutePaths.Settings)
            // }
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
        {config.version ? (
          <li>
            <Version primary />
          </li>
        ) : null}
      </Menu>
    </Bar>
  );
};

export default SideBar;
