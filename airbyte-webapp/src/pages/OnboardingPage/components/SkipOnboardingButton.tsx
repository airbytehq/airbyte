import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button } from "components";
import useWorkspace from "hooks/services/useWorkspace";

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
    <ButtonWithMargin
      onClick={onSkip}
      secondary
      type="button"
      data-id="skip-onboarding"
    >
      <FormattedMessage id="onboarding.skipOnboarding" />
    </ButtonWithMargin>
  );
};

export default SkipOnboardingButton;
