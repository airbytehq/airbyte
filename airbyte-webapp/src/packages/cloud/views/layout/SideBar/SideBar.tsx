import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { faEnvelope } from "@fortawesome/free-regular-svg-icons";
import { faDesktop, faQuestionCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage, FormattedNumber, useIntl } from "react-intl";
import { NavLink } from "react-router-dom";

import { Link } from "components";
import { CreditsIcon } from "components/icons/CreditsIcon";
import { DocsIcon } from "components/icons/DocsIcon";
import { Text } from "components/ui/Text";

import { useExperiment } from "hooks/services/Experiment";
import { FeatureItem, IfFeatureEnabled } from "hooks/services/Feature";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { useIntercom } from "packages/cloud/services/thirdParty/intercom";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { WorkspacePopout } from "packages/cloud/views/workspaces/WorkspacePopout";
import { links } from "utils/links";
import { ReactComponent as AirbyteLogo } from "views/layout/SideBar/airbyteLogo.svg";
import ChatIcon from "views/layout/SideBar/components/ChatIcon";
import ConnectionsIcon from "views/layout/SideBar/components/ConnectionsIcon";
import DestinationIcon from "views/layout/SideBar/components/DestinationIcon";
import OnboardingIcon from "views/layout/SideBar/components/OnboardingIcon";
import SettingsIcon from "views/layout/SideBar/components/SettingsIcon";
import { SidebarDropdownMenu, SidebarDropdownMenuItemType } from "views/layout/SideBar/components/SidebarDropdownMenu";
import SourceIcon from "views/layout/SideBar/components/SourceIcon";
import StatusIcon from "views/layout/SideBar/components/StatusIcon";
import { NotificationIndicator } from "views/layout/SideBar/NotificationIndicator";
import { useCalculateSidebarStyles } from "views/layout/SideBar/SideBar";

import { RoutePaths } from "../../../../../pages/routePaths";
import styles from "./SideBar.module.scss";

const SideBar: React.FC = () => {
  const navLinkClassName = useCalculateSidebarStyles();
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);
  const { show } = useIntercom();
  const handleChatUs = () => show();
  const hideOnboardingExperiment = useExperiment("onboarding.hideOnboarding", false);
  const { formatMessage } = useIntl();

  return (
    <nav className={styles.nav}>
      <div>
        <Link
          to={
            workspace.displaySetupWizard && !hideOnboardingExperiment ? RoutePaths.Onboarding : RoutePaths.Connections
          }
          aria-label={formatMessage({ id: "sidebar.homepage" })}
        >
          <AirbyteLogo height={33} width={33} />
        </Link>
        <WorkspacePopout>
          {({ onOpen, value }) => (
            <button className={styles.workspaceButton} onClick={onOpen}>
              {value}
            </button>
          )}
        </WorkspacePopout>
        <ul className={styles.menu}>
          {workspace.displaySetupWizard && !hideOnboardingExperiment ? (
            <li>
              <NavLink className={navLinkClassName} to={RoutePaths.Onboarding}>
                <OnboardingIcon />
                <Text className={styles.text} size="sm">
                  <FormattedMessage id="sidebar.onboarding" />
                </Text>
              </NavLink>
            </li>
          ) : null}
          <li>
            <NavLink className={navLinkClassName} to={RoutePaths.Connections}>
              <ConnectionsIcon />
              <Text className={styles.text} size="sm">
                <FormattedMessage id="sidebar.connections" />
              </Text>
            </NavLink>
          </li>
          <li>
            <NavLink className={navLinkClassName} to={RoutePaths.Source}>
              <SourceIcon />
              <Text className={styles.text} size="sm">
                <FormattedMessage id="sidebar.sources" />
              </Text>
            </NavLink>
          </li>
          <li>
            <NavLink className={navLinkClassName} to={RoutePaths.Destination}>
              <DestinationIcon />
              <Text className={styles.text} size="sm">
                <FormattedMessage id="sidebar.destinations" />
              </Text>
            </NavLink>
          </li>
        </ul>
      </div>
      <ul className={styles.menu}>
        <li>
          <NavLink className={navLinkClassName} to={CloudRoutes.Credits}>
            <CreditsIcon />
            <Text className={styles.text} size="sm">
              <FormattedNumber value={cloudWorkspace.remainingCredits} />
            </Text>
          </NavLink>
        </li>
        <li>
          <SidebarDropdownMenu
            label={{ icon: <DocsIcon />, displayName: <FormattedMessage id="sidebar.resources" /> }}
            options={[
              {
                type: SidebarDropdownMenuItemType.LINK,
                href: links.docsLink,
                icon: <DocsIcon />,
                displayName: <FormattedMessage id="sidebar.documentation" />,
              },
              {
                type: SidebarDropdownMenuItemType.LINK,
                href: links.slackLink,
                icon: <FontAwesomeIcon icon={faSlack} />,
                displayName: <FormattedMessage id="sidebar.joinSlack" />,
              },
              {
                type: SidebarDropdownMenuItemType.LINK,
                href: links.statusLink,
                icon: <StatusIcon />,
                displayName: <FormattedMessage id="sidebar.status" />,
              },
              {
                type: SidebarDropdownMenuItemType.LINK,
                href: links.demoLink,
                icon: <FontAwesomeIcon icon={faDesktop} />,
                displayName: <FormattedMessage id="sidebar.demo" />,
              },
            ]}
          />
        </li>
        <li>
          <SidebarDropdownMenu
            label={{
              icon: <FontAwesomeIcon icon={faQuestionCircle} size="2x" />,
              displayName: <FormattedMessage id="sidebar.support" />,
            }}
            options={[
              {
                type: SidebarDropdownMenuItemType.LINK,
                href: links.supportTicketLink,
                icon: <FontAwesomeIcon icon={faEnvelope} />,
                displayName: <FormattedMessage id="sidebar.supportTicket" />,
              },
              {
                type: SidebarDropdownMenuItemType.BUTTON,
                onClick: handleChatUs,
                icon: <ChatIcon />,
                displayName: <FormattedMessage id="sidebar.chat" />,
              },
            ]}
          />
        </li>
        <li>
          <NavLink className={navLinkClassName} to={RoutePaths.Settings}>
            <IfFeatureEnabled feature={FeatureItem.AllowUpdateConnectors}>
              <React.Suspense fallback={null}>
                <NotificationIndicator />
              </React.Suspense>
            </IfFeatureEnabled>
            <SettingsIcon />
            <Text className={styles.text} size="sm">
              <FormattedMessage id="sidebar.settings" />
            </Text>
          </NavLink>
        </li>
      </ul>
    </nav>
  );
};

export default SideBar;
