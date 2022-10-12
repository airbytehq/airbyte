import React from "react";
import { FormattedMessage } from "react-intl";

import { PageViewContainer } from "components/CenteredPageComponents";
import HeadTitle from "components/HeadTitle";
import { Text } from "components/ui/Text";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import useWorkspace from "hooks/services/useWorkspace";
import { PreferencesForm } from "views/Settings/PreferencesForm";

import styles from "./PreferencesPage.module.scss";

const PreferencesPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.PREFERENCES);

  const { setInitialSetupConfig } = useWorkspace();

  return (
    <PageViewContainer>
      <HeadTitle titles={[{ id: "preferences.headTitle" }]} />
      <Text as="h1" size="lg" centered className={styles.title}>
        <FormattedMessage id="preferences.title" />
      </Text>
      <PreferencesForm onSubmit={setInitialSetupConfig} />
    </PageViewContainer>
  );
};

export default PreferencesPage;
