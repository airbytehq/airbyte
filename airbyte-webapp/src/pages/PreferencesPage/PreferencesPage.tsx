import React from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import { PageViewContainer } from "../../components/CenteredPageComponents";
import { H1 } from "../../components/Titles";
import PreferencesForm from "./components/PreferencesForm";
import WorkspaceResource from "../../core/resources/Workspace";
import config from "../../config";

const PreferencesPage: React.FC = () => {
  const updateWorkspace = useFetcher(WorkspaceResource.updateShape());

  const onSubmit = async (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => {
    await updateWorkspace(
      {},
      {
        workspaceId: config.ui.workspaceId,
        initialSetupComplete: true,
        ...data
      }
    );
  };

  return (
    <PageViewContainer>
      <H1 center>
        <FormattedMessage id={"preferences.title"} />
      </H1>
      <PreferencesForm onSubmit={onSubmit} />
    </PageViewContainer>
  );
};

export default PreferencesPage;
