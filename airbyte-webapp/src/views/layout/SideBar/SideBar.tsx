import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRocket, faBook, faCog } from "@fortawesome/free-solid-svg-icons";
import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { FormattedMessage } from "react-intl";
import { NavLink } from "react-router-dom";

import { Routes } from "pages/routes";
import { useConfig } from "config";

import useConnector from "hooks/services/useConnector";
import { Link } from "components";
import Version from "components/Version";
import Indicator from "components/Indicator";

import Source from "./components/SourceIcon";
import Connections from "./components/ConnectionsIcon";
import Destination from "./components/DestinationIcon";
import Onboarding from "./components/OnboardingIcon";
import useWorkspace from "hooks/services/useWorkspace";

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

const SideBar: React.FC = () => {
  const { hasNewVersions } = useConnector();
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
                <Onboarding />
                <Text>
                  <FormattedMessage id="sidebar.onboarding" />
                </Text>
              </MenuItem>
            </li>
          ) : null}
          <li>
            <MenuItem to={Routes.Connections} activeClassName="active">
              <Connections />
              <Text>
                <FormattedMessage id="sidebar.connections" />
              </Text>
            </MenuItem>
          </li>
          <li>
            <MenuItem to={Routes.Source} activeClassName="active">
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
            <DocsIcon icon={faBook} />
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
