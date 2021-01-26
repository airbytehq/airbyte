import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Button from "../../../components/Button";
import useWorkspace from "../../../components/hooks/services/useWorkspaceHook";

const ButtonWithMargin = styled(Button)`
  margin-right: 9px;
`;

type IProps = {
  step: string;
};

const SkipOnboardingButton: React.FC<IProps> = ({ step }) => {
  const { finishOnboarding } = useWorkspace();

  const onSkip = async () => {
    await finishOnboarding(step);
  };

  return (
    <ButtonWithMargin onClick={onSkip} secondary type="button">
      <FormattedMessage id="onboarding.skipOnboarding" />
    </ButtonWithMargin>
  );
};

export default SkipOnboardingButton;
