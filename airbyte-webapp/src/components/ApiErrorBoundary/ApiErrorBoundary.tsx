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
  hideHeader?: boolean;
}

interface ApiErrorBoundaryHookProps {
  location: LocationSensorState;
  onRetry?: () => void;
}

class ApiErrorBoundary extends React.Component<
  ApiErrorBoundaryProps & ApiErrorBoundaryHookProps,
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
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  componentDidCatch(): void {}

  render(): React.ReactNode {
    const { errorId, didRetry, message } = this.state;
    const { onRetry, hideHeader, children } = this.props;

    if (errorId === ErrorId.VersionMismatch) {
      return <ErrorOccurredView message={message} />;
    }

    if (errorId === ErrorId.ServerUnavailable && !didRetry) {
      return (
        <ErrorOccurredView message={<FormattedMessage id="webapp.cannotReachServer" />} hideHeader={hideHeader}>
          {onRetry && (
            <RetryContainer>
              <Button
                onClick={() => {
                  this.setState({ didRetry: true, errorId: undefined });
                  onRetry?.();
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
      <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView hideHeader={hideHeader} />}>
        {children}
      </ResourceNotFoundErrorBoundary>
    ) : (
      <ErrorOccurredView message={<FormattedMessage id="errorView.unknownError" />} hideHeader={hideHeader} />
    );
  }
}

const ApiErrorBoundaryWithHooks: React.FC<ApiErrorBoundaryProps> = ({ children, hideHeader }) => {
  const { reset } = useQueryErrorResetBoundary();
  const location = useLocation();

  return (
    <ApiErrorBoundary location={location} onRetry={reset} hideHeader={hideHeader}>
      {children}
    </ApiErrorBoundary>
  );
};

export default ApiErrorBoundaryWithHooks;
