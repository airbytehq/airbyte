import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRocket } from "@fortawesome/free-solid-svg-icons";
import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { FormattedMessage } from "react-intl";
import { NavLink } from "react-router-dom";

import { Routes } from "pages/routes";
import { useConfig } from "config";
import useWorkspace from "hooks/services/useWorkspace";

import { Link } from "components";
import Version from "components/Version";

import ConnectionsIcon from "./components/ConnectionsIcon";
import DestinationIcon from "./components/DestinationIcon";
import DocsIcon from "./components/DocsIcon";
import OnboardingIcon from "./components/OnboardingIcon";
import SettingsIcon from "./components/SettingsIcon";
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
  const { workspace } = useWorkspace();

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
      </div>
      <Menu>
        <li>
          <MenuLinkItem href={config.ui.updateLink} target="_blank">
            <HelpIcon icon={faRocket} />
            <Text>
              <FormattedMessage id="sidebar.update" />
            </Text>
          </MenuLinkItem>
        </li>
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
            <DocsIcon />
            <Text>
              <FormattedMessage id="sidebar.docs" />
            </Text>
          </MenuLinkItem>
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
