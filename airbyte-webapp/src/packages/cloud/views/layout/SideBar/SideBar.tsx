import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { faEnvelope } from "@fortawesome/free-regular-svg-icons";
import { faQuestionCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { NavLink } from "react-router-dom";
import { useIntercom } from "react-use-intercom";

import { Link } from "components";
import { CreditsIcon } from "components/icons/CreditsIcon";

import { FeatureItem, IfFeatureEnabled } from "hooks/services/Feature";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/WorkspacesService";
import { WorkspacePopout } from "packages/cloud/views/workspaces/WorkspacePopout";
import ConnectionsIcon from "views/layout/SideBar/components/ConnectionsIcon";
import DestinationIcon from "views/layout/SideBar/components/DestinationIcon";
import OnboardingIcon from "views/layout/SideBar/components/OnboardingIcon";
import SettingsIcon from "views/layout/SideBar/components/SettingsIcon";
import SourceIcon from "views/layout/SideBar/components/SourceIcon";
import { NotificationIndicator } from "views/layout/SideBar/NotificationIndicator";
import { useCalculateSidebarStyles } from "views/layout/SideBar/SideBar";

import { useConfig } from "../../../../../config";
import { RoutePaths } from "../../../../../pages/routePaths";
import ChatIcon from "../../../../../views/layout/SideBar/components/ChatIcon";
import DocsIcon from "../../../../../views/layout/SideBar/components/DocsIcon";
import RecipesIcon from "../../../../../views/layout/SideBar/components/RecipesIcon";
import { SidebarDropdownMenu } from "../../../../../views/layout/SideBar/components/SidebarDropdownMenu";
import StatusIcon from "../../../../../views/layout/SideBar/components/StatusIcon";
import styles from "./SideBar.module.scss";

const SideBar: React.FC = () => {
  const navLinkClassName = useCalculateSidebarStyles();
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);
  const config = useConfig();
  const { show } = useIntercom();
  const handleChatUs = () => show();

  return (
    <nav className={styles.navBar}>
      <div>
        <Link to={workspace.displaySetupWizard ? RoutePaths.Onboarding : RoutePaths.Connections}>
          <img src="/simpleLogo.svg" alt="logo" height={33} width={33} />
        </Link>
        <WorkspacePopout>
          {({ onOpen, value }) => (
            <div className={styles.workspaceButton} onClick={onOpen}>
              {value}
            </div>
          )}
        </WorkspacePopout>
        <div className={styles.menu}>
          {workspace.displaySetupWizard ? (
            <div>
              <NavLink className={navLinkClassName} to={RoutePaths.Onboarding}>
                <OnboardingIcon />
                <span className={styles.text}>
                  <FormattedMessage id="sidebar.onboarding" />
                </span>
              </NavLink>
            </div>
          ) : null}
          <div>
            <NavLink className={navLinkClassName} to={RoutePaths.Connections}>
              <ConnectionsIcon />
              <span className={styles.text}>
                <FormattedMessage id="sidebar.connections" />
              </span>
            </NavLink>
          </div>
          <div>
            <NavLink className={navLinkClassName} to={RoutePaths.Source}>
              <SourceIcon />
              <span className={styles.text}>
                <FormattedMessage id="sidebar.sources" />
              </span>
            </NavLink>
          </div>
          <div>
            <NavLink className={navLinkClassName} to={RoutePaths.Destination}>
              <DestinationIcon />
              <span className={styles.text}>
                <FormattedMessage id="sidebar.destinations" />
              </span>
            </NavLink>
          </div>
        </div>
      </div>
      <div className={styles.menu}>
        <div>
          <NavLink className={navLinkClassName} to={CloudRoutes.Credits}>
            <CreditsIcon />
            <span className={styles.text}>
              <FormattedNumber value={cloudWorkspace.remainingCredits} />
            </span>
          </NavLink>
        </div>
        <div>
          <SidebarDropdownMenu
            options={[
              <a href={config.links.docsLink} target="_blank" rel="noreferrer">
                <span>
                  <DocsIcon />
                </span>
                <FormattedMessage id="sidebar.documentation" />
              </a>,
              <a href={config.links.slackLink} target="_blank" rel="noreferrer">
                <span>
                  <FontAwesomeIcon icon={faSlack} />
                </span>
                <FormattedMessage id="sidebar.joinSlack" />
              </a>,
              <a href={config.links.statusLink} target="_blank" rel="noreferrer">
                <span>
                  <StatusIcon />
                </span>
                <FormattedMessage id="sidebar.status" />
              </a>,
              <a href={config.links.recipesLink} target="_blank" rel="noreferrer">
                <span>
                  <RecipesIcon />
                </span>
                <FormattedMessage id="sidebar.recipes" />
              </a>,
            ]}
          >
            <DocsIcon />
            <span>
              <FormattedMessage id="sidebar.resources" />
            </span>
          </SidebarDropdownMenu>
        </div>
        <div>
          <SidebarDropdownMenu
            options={[
              <a href={config.links.supportTicketLink} target="_blank" rel="noreferrer">
                <span>
                  <FontAwesomeIcon icon={faEnvelope} />
                </span>
                <FormattedMessage id="sidebar.supportTicket" />
              </a>,
              <div onClick={handleChatUs}>
                <span>
                  <ChatIcon />
                </span>
                <FormattedMessage id="sidebar.chat" />
              </div>,
            ]}
          >
            <FontAwesomeIcon icon={faQuestionCircle} size="2x" />
            <span>
              <FormattedMessage id="sidebar.support" />
            </span>
          </SidebarDropdownMenu>
        </div>
        <div>
          <NavLink className={navLinkClassName} to={RoutePaths.Settings}>
            <IfFeatureEnabled feature={FeatureItem.AllowUpdateConnectors}>
              <React.Suspense fallback={null}>
                <NotificationIndicator />
              </React.Suspense>
            </IfFeatureEnabled>
            <SettingsIcon />
            <span className={styles.text}>
              <FormattedMessage id="sidebar.settings" />
            </span>
          </NavLink>
        </div>
      </div>
    </nav>
  );
};

export default SideBar;
