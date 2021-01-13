import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import Button from "../../../components/Button";
import WorkspaceResource from "../../../core/resources/Workspace";
import { useResource } from "rest-hooks/lib/react-integration/hooks";
import config from "../../../config";

const ButtonWithMargin = styled(Button)`
  margin-right: 9px;
`;

const SkipOnboardingButton: React.FC = () => {
  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: config.ui.workspaceId
  });
  const updateWorkspace = useFetcher(WorkspaceResource.updateShape());
  const onSkip = async () => {
    await updateWorkspace(
      {},
      {
        workspaceId: workspace.workspaceId,
        initialSetupComplete: workspace.initialSetupComplete,
        displaySetupWizard: false,
        anonymousDataCollection: workspace.anonymousDataCollection,
        securityUpdates: workspace.securityUpdates,
        news: workspace.news
      }
    );
  };

  return (
    <ButtonWithMargin onClick={onSkip} secondary type="button">
      <FormattedMessage id="onboarding.skipOnboarding" />
    </ButtonWithMargin>
  );
};

export default SkipOnboardingButton;
