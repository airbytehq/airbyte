import React from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { ErrorOccurredView } from "views/common/ErrorOccurredView";

interface StartOverErrorViewProps {
  message?: string;
  onReset?: () => void;
}

export const StartOverErrorView: React.FC<StartOverErrorViewProps> = ({ message, onReset }) => {
  const navigate = useNavigate();

  return (
    <ErrorOccurredView
      message={message ?? <FormattedMessage id="errorView.notFound" />}
      ctaButtonText={<FormattedMessage id="ui.goBack" />}
      onCtaButtonClick={() => {
        onReset?.();
        navigate("..");
      }}
    />
  );
};
