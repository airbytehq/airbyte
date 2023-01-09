import React, { useEffect } from "react";
import { FormattedMessage } from "react-intl";

import { ErrorOccurredView } from "views/common/ErrorOccurredView";

interface ServerUnavailableViewProps {
  onRetryClick: () => void;
  retryDelay: number;
}

export const ServerUnavailableView: React.FC<ServerUnavailableViewProps> = ({ onRetryClick, retryDelay }) => {
  useEffect(() => {
    const timer: ReturnType<typeof setTimeout> = setTimeout(() => {
      onRetryClick();
    }, retryDelay);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <ErrorOccurredView
      message={<FormattedMessage id="webapp.cannotReachServer" />}
      ctaButtonText={<FormattedMessage id="errorView.retry" />}
      onCtaButtonClick={onRetryClick}
    />
  );
};
