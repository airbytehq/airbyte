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

import { ServerUnavailableView } from "./ServerUnavailableView";

interface ApiErrorBoundaryState {
  errorId?: string;
  message?: string;
  didRetry?: boolean;
  retryDelay?: number;
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

const RETRY_DELAY = 2500;

class ApiErrorBoundaryComponent extends React.Component<
  React.PropsWithChildren<ApiErrorBoundaryHookProps & ApiErrorBoundaryProps>,
  ApiErrorBoundaryState
> {
  state: ApiErrorBoundaryState = {
    retryDelay: RETRY_DELAY,
  };

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

  retry = () => {
    this.setState((state) => ({
      didRetry: true,
      errorId: undefined,
      retryDelay: Math.round((state?.retryDelay || RETRY_DELAY) * 1.2),
    }));
    this.props.onRetry?.();
  };

  render(): React.ReactNode {
    const { navigate, children } = this.props;
    const { errorId, didRetry, message, retryDelay } = this.state;

    if (errorId === ErrorId.VersionMismatch) {
      return <ErrorOccurredView message={message} />;
    }

    if (errorId === ErrorId.ServerUnavailable && !didRetry) {
      return <ServerUnavailableView retryDelay={retryDelay || RETRY_DELAY} onRetryClick={this.retry} />;
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

export const ApiErrorBoundary: React.FC<React.PropsWithChildren<ApiErrorBoundaryProps>> = ({ children, ...props }) => {
  const { reset } = useQueryErrorResetBoundary();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <ApiErrorBoundaryComponent {...props} location={location} navigate={navigate} onRetry={reset}>
      {children}
    </ApiErrorBoundaryComponent>
  );
};
