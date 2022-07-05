import React from "react";
import { FormattedMessage } from "react-intl";
import { useQueryErrorResetBoundary } from "react-query";
import { NavigateFunction, useNavigate } from "react-router-dom";
import { useLocation } from "react-use";
import { LocationSensorState } from "react-use/lib/useLocation";

import { isVersionError } from "core/request/VersionError";
import { ErrorOccurredView } from "views/common/ErrorOccurredView";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

interface ApiErrorBoundaryState {
  errorId?: string;
  message?: string;
  didRetry?: boolean;
}

enum ErrorId {
  VersionMismatch = "version.mismatch",
  ServerUnavailable = "server.unavailable",
  UnknownError = "unknown",
}

interface ApiErrorBoundaryHookProps {
  location: LocationSensorState;
  onRetry?: () => void;
  navigate: NavigateFunction;
}

interface ApiErrorBoundaryProps {
  onError?: (errorId?: string) => void;
}

class ApiErrorBoundary extends React.Component<
  ApiErrorBoundaryHookProps & ApiErrorBoundaryProps,
  ApiErrorBoundaryState
> {
  state: ApiErrorBoundaryState = {};

  static getDerivedStateFromError(error: { message: string; status?: number; __type?: string }): ApiErrorBoundaryState {
    // Update state so the next render will show the fallback UI.
    if (isVersionError(error)) {
      return { errorId: ErrorId.VersionMismatch, message: error.message };
    }

    const isNetworkBoundaryMessage = error.message === "Failed to fetch";
    const is502 = error.status === 502;

    if (isNetworkBoundaryMessage || is502) {
      return { errorId: ErrorId.ServerUnavailable, didRetry: false };
    }

    return { errorId: ErrorId.UnknownError, didRetry: false };
  }

  componentDidUpdate(prevProps: ApiErrorBoundaryHookProps) {
    const { location } = this.props;

    if (location !== prevProps.location) {
      this.setState({ errorId: undefined, didRetry: false });
      this.props.onError?.(undefined);
    } else {
      this.props.onError?.(this.state.errorId);
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  componentDidCatch(): void {}

  render(): React.ReactNode {
    const { errorId, didRetry, message } = this.state;
    const { onRetry, navigate, children } = this.props;

    if (errorId === ErrorId.VersionMismatch) {
      return <ErrorOccurredView message={message} />;
    }

    if (errorId === ErrorId.ServerUnavailable && !didRetry) {
      return (
        <ErrorOccurredView
          message={<FormattedMessage id="webapp.cannotReachServer" />}
          ctaButtonText={<FormattedMessage id="errorView.retry" />}
          onCtaButtonClick={() => {
            this.setState({ didRetry: true, errorId: undefined });
            onRetry?.();
          }}
        />
      );
    }

    return !errorId ? (
      <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>{children}</ResourceNotFoundErrorBoundary>
    ) : (
      <ErrorOccurredView
        message={<FormattedMessage id="errorView.unknownError" />}
        ctaButtonText={<FormattedMessage id="ui.goBack" />}
        onCtaButtonClick={() => {
          navigate("..");
        }}
      />
    );
  }
}

const ApiErrorBoundaryWithHooks: React.FC<ApiErrorBoundaryProps> = ({ children, ...props }) => {
  const { reset } = useQueryErrorResetBoundary();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <ApiErrorBoundary {...props} location={location} navigate={navigate} onRetry={reset}>
      {children}
    </ApiErrorBoundary>
  );
};

export default ApiErrorBoundaryWithHooks;
