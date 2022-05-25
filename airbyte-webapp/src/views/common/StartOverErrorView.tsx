import React from "react";
import { FormattedMessage } from "react-intl";

import { ErrorOccurredView } from "views/common/ErrorOccurredView";

interface StartOverErrorViewProps {
  message?: string;
  onReset?: () => void;
}

export const StartOverErrorView: React.FC<StartOverErrorViewProps> = ({ message, onReset }) => {
  return (
    <ErrorOccurredView
      message={message ?? <FormattedMessage id="errorView.notFound" />}
      ctaButtonText={<FormattedMessage id="errorView.home" />}
      onCtaButtonClick={() => {
        onReset?.();
      }}
    />
  );
};
