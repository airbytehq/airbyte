import React from "react";
import { FormattedMessage } from "react-intl";
import { useQueryErrorResetBoundary } from "react-query";
import { useLocation } from "react-use";
import { LocationSensorState } from "react-use/lib/useLocation";
import styled from "styled-components";

import { Button } from "components/base/Button";

import { isVersionError } from "core/request/VersionError";
import { ErrorOccurredView } from "views/common/ErrorOccurredView";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

const RetryContainer = styled.div`
  margin-top: 20px;
  display: flex;
  justify-content: center;
`;

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

interface ApiErrorBoundaryProps {
  /**
   * If the error should clear out when the user navigates to another page
   */
  resetOnLocationChange?: boolean;
  /**
   * Whether the user should be allowed to retry the request
   */
  withRetry?: boolean;
}

interface ApiErrorBoundaryHooks {
  location: LocationSensorState;
  onRetry?: () => void;
}

class ApiErrorBoundary extends React.Component<ApiErrorBoundaryProps & ApiErrorBoundaryHooks, ApiErrorBoundaryState> {
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

  componentDidUpdate(prevProps: ApiErrorBoundaryProps & ApiErrorBoundaryHooks) {
    const { location, resetOnLocationChange } = this.props;

    if (resetOnLocationChange && location !== prevProps.location) {
      this.setState({ errorId: undefined, didRetry: false });
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  componentDidCatch(): void {}

  render(): React.ReactNode {
    const { errorId, didRetry, message } = this.state;
    const { withRetry, onRetry, children } = this.props;

    if (errorId === ErrorId.VersionMismatch) {
      return <ErrorOccurredView message={message} />;
    }

    if (errorId === ErrorId.ServerUnavailable && !didRetry) {
      return (
        <ErrorOccurredView message={<FormattedMessage id="webapp.cannotReachServer" />}>
          {withRetry && onRetry && (
            <RetryContainer>
              <Button
                onClick={() => {
                  this.setState({ didRetry: true, errorId: undefined }, () => onRetry?.());
                }}
              >
                <FormattedMessage id="errorView.retry" />
              </Button>
            </RetryContainer>
          )}
        </ErrorOccurredView>
      );
    }

    return !errorId ? (
      <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>{children}</ResourceNotFoundErrorBoundary>
    ) : (
      <ErrorOccurredView message={<FormattedMessage id="errorView.unknownError" />} />
    );
  }
}

const ApiErrorBoundaryWithHooks: React.FC<ApiErrorBoundaryProps> = ({ children, ...props }) => {
  const { reset } = useQueryErrorResetBoundary();
  const location = useLocation();

  return (
    <ApiErrorBoundary {...props} location={location} onRetry={reset}>
      {children}
    </ApiErrorBoundary>
  );
};

export default ApiErrorBoundaryWithHooks;
