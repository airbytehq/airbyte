import { faSlack } from "@fortawesome/free-brands-svg-icons";
import { faCircleQuestion, faEnvelope } from "@fortawesome/free-regular-svg-icons";
import { faDesktop } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { NavLink } from "react-router-dom";

import { Link } from "components";
import { CreditsIcon } from "components/icons/CreditsIcon";
import { DocsIcon } from "components/icons/DocsIcon";
import { Indicator } from "components/Indicator/Indicator";
import { DropdownMenu, DropdownMenuOptionType } from "components/ui/DropdownMenu";
import { Text } from "components/ui/Text";

import { FeatureItem, IfFeatureEnabled } from "hooks/services/Feature";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { CloudRoutes } from "packages/cloud/cloudRoutePaths";
import { useIntercom } from "packages/cloud/services/thirdParty/intercom";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { WorkspacePopout } from "packages/cloud/views/workspaces/WorkspacePopout";
import { links } from "utils/links";
import { ReactComponent as AirbyteLogo } from "views/layout/SideBar/airbyteLogo.svg";
import ChatIcon from "views/layout/SideBar/components/ChatIcon";
import ConnectionsIcon from "views/layout/SideBar/components/ConnectionsIcon";
import DestinationIcon from "views/layout/SideBar/components/DestinationIcon";
import SettingsIcon from "views/layout/SideBar/components/SettingsIcon";
import SourceIcon from "views/layout/SideBar/components/SourceIcon";
import StatusIcon from "views/layout/SideBar/components/StatusIcon";
import { NotificationIndicator } from "views/layout/SideBar/NotificationIndicator";
import { useCalculateSidebarStyles } from "views/layout/SideBar/SideBar";

import styles from "./SideBar.module.scss";
import { RoutePaths } from "../../../../../pages/routePaths";
import { LOW_BALANCE_CREDIT_TRESHOLD } from "../../credits/CreditsPage/components/LowCreditBalanceHint/LowCreditBalanceHint";

const SideBar: React.FC = () => {
  const navLinkClassName = useCalculateSidebarStyles();
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);
  const { show } = useIntercom();
  const { formatMessage } = useIntl();
  const handleChatUs = (data: DropdownMenuOptionType) => data.value === "chatUs" && show();

  return (
    <nav className={styles.nav}>
      <div>
        <Link to={RoutePaths.Connections} aria-label={formatMessage({ id: "sidebar.homepage" })}>
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
        <li className={styles.creditsButton}>
          <NavLink className={navLinkClassName} to={CloudRoutes.Credits}>
            {cloudWorkspace.remainingCredits <= LOW_BALANCE_CREDIT_TRESHOLD && (
              <Indicator className={styles.lowBalanceIndicator} />
            )}
            <CreditsIcon />
            <Text className={styles.text} size="sm">
              <FormattedMessage id="sidebar.credits" />
            </Text>
          </NavLink>
        </li>
        <li>
          <DropdownMenu
            placement="right"
            displacement={10}
            options={[
              {
                as: "a",
                href: links.docsLink,
                icon: <DocsIcon />,
                displayName: formatMessage({ id: "sidebar.documentation" }),
              },
              {
                as: "a",
                href: links.slackLink,
                icon: <FontAwesomeIcon icon={faSlack} />,
                displayName: formatMessage({ id: "sidebar.joinSlack" }),
              },
              {
                as: "a",
                href: links.statusLink,
                icon: <StatusIcon />,
                displayName: formatMessage({ id: "sidebar.status" }),
              },
              {
                as: "a",
                href: links.demoLink,
                icon: <FontAwesomeIcon icon={faDesktop} />,
                displayName: formatMessage({ id: "sidebar.demo" }),
              },
            ]}
          >
            {({ open }) => (
              <button className={classNames(styles.dropdownMenuButton, { [styles.open]: open })}>
                <DocsIcon />
                <Text className={styles.text} size="sm">
                  <FormattedMessage id="sidebar.resources" />
                </Text>
              </button>
            )}
          </DropdownMenu>
        </li>
        <li>
          <DropdownMenu
            placement="right"
            displacement={10}
            options={[
              {
                as: "a",
                href: links.supportTicketLink,
                icon: <FontAwesomeIcon icon={faEnvelope} />,
                displayName: formatMessage({ id: "sidebar.supportTicket" }),
              },
              {
                as: "button",
                icon: <ChatIcon />,
                value: "chatUs",
                displayName: formatMessage({ id: "sidebar.chat" }),
              },
            ]}
            onChange={handleChatUs}
          >
            {({ open }) => (
              <button className={classNames(styles.dropdownMenuButton, { [styles.open]: open })}>
                <FontAwesomeIcon icon={faCircleQuestion} size="2x" />
                <Text className={styles.text} size="sm">
                  <FormattedMessage id="sidebar.support" />
                </Text>
              </button>
            )}
          </DropdownMenu>
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
