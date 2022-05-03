import React from "react";
import { FormattedMessage } from "react-intl";

import useRouter from "hooks/useRouter";
import { ErrorOccurredView } from "views/common/ErrorOccurredView";

export const StartOverErrorView: React.FC<{
  message?: string;
  onReset?: () => void;
}> = ({ message, onReset }) => {
  const { push } = useRouter();
  return (
    <ErrorOccurredView
      message={message ?? <FormattedMessage id="errorView.notFound" />}
      onLogoClick={() => {
        push("..");
        onReset?.();
      }}
    />
  );
};
