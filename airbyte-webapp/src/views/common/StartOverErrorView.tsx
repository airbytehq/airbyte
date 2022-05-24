import React from "react";
import { FormattedMessage } from "react-intl";

import { ErrorOccurredView } from "views/common/ErrorOccurredView";

interface StartOverErrorViewProps {
  message?: string;
  onReset?: () => void;
  hideHeader?: boolean;
}

export const StartOverErrorView: React.FC<StartOverErrorViewProps> = ({ message, onReset, hideHeader }) => {
  return (
    <ErrorOccurredView
      message={message ?? <FormattedMessage id="errorView.notFound" />}
      onBackClick={() => {
        onReset?.();
      }}
      hideHeader={hideHeader}
    />
  );
};
