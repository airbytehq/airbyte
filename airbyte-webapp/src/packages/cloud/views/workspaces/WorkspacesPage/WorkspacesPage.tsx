import React from "react";
import { FormattedMessage } from "react-intl";

import { Text } from "components/base/Text";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";

import WorkspacesList from "./components/WorkspacesList";
import styles from "./WorkspacesPage.module.scss";

const WorkspacesPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.WORKSPACES);

  return (
    <div className={styles.container}>
      <img className={styles.logo} alt="logo" src="/cloud-main-logo.svg" width={186} />
      <Text as="h1" size="lg" centered>
        <FormattedMessage id="workspaces.title" />
      </Text>
      <Text as="p" centered className={styles.subtitle}>
        <FormattedMessage id="workspaces.subtitle" />
      </Text>
      <WorkspacesList />
    </div>
  );
};

export default WorkspacesPage;
