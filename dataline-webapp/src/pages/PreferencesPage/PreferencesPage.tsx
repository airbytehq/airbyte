import React from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import { PageViewContainer } from "../../components/CenteredPageComponents";
import { H1 } from "../../components/Titles";
import { Routes } from "../routes";
import useRouter from "../../components/hooks/useRouterHook";
import PreferencesForm from "./components/PreferencesForm";
import WorkspaceResource from "../../core/resources/Workspace";

const PreferencesPage: React.FC = () => {
  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: "1"
  });

  console.log(workspace);

  const { push } = useRouter();
  const onSubmit = () => push(Routes.Onboarding); // TODO: add real onSubmit

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
