import React from "react";
import { FormattedMessage } from "react-intl";

import { PageViewContainer } from "../../components/CenteredPageComponents";
import { H1 } from "../../components/Titles";
import { Routes } from "../routes";
import useRouter from "../../components/hooks/useRouterHook";
import PreferencesForm from "./components/PreferencesForm";

const PreferencesPage: React.FC = () => {
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
