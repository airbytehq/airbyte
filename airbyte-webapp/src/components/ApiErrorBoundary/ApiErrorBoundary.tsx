import React from "react";
import { FormattedMessage } from "react-intl";
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
  wasReset?: boolean;
}

enum ErrorId {
  VersionMismatch = "version.mismatch",
  ServerUnavailable = "server.unavailable",
  UnknownError = "unknown",
}

interface ApiErrorBoundaryProps {
  onReset?: () => void;
  clearOnLocationChange?: boolean;
  location: LocationSensorState;
}

class ApiErrorBoundary extends React.Component<ApiErrorBoundaryProps, ApiErrorBoundaryState> {
  state: ApiErrorBoundaryState = {};

  static getDerivedStateFromError(error: { message: string; status?: number; __type?: string }): ApiErrorBoundaryState {
    // Update state so the next render will show the fallback UI.
    if (isVersionError(error)) {
      return { errorId: ErrorId.VersionMismatch, message: error.message };
    }

    const isNetworkBoundaryMessage = error.message === "Failed to fetch";
    const is502 = error.status === 502;

    if (isNetworkBoundaryMessage || is502) {
      return { errorId: ErrorId.ServerUnavailable, wasReset: false };
    }

    return { errorId: ErrorId.UnknownError, wasReset: false };
  }

  componentDidUpdate(prevProps: ApiErrorBoundaryProps) {
    const { location, clearOnLocationChange } = this.props;

    if (clearOnLocationChange && location !== prevProps.location) {
      this.setState({ errorId: undefined, wasReset: false });
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  componentDidCatch(): void {}

  render(): React.ReactNode {
    const { errorId, wasReset, message } = this.state;
    const { onReset, children } = this.props;

    if (errorId === ErrorId.VersionMismatch) {
      return <ErrorOccurredView message={message} />;
    }

    if (errorId === ErrorId.ServerUnavailable && !wasReset) {
      return (
        <ErrorOccurredView message={<FormattedMessage id="webapp.cannotReachServer" />}>
          {onReset && (
            <RetryContainer>
              <Button
                onClick={() => {
                  this.setState({ wasReset: true, errorId: undefined }, () => onReset?.());
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

function withLocation<P>(Component: React.ComponentType<P>) {
  return ({ children, ...props }: React.PropsWithChildren<Omit<P, "location">>) => {
    const location = useLocation();
    return (
      <Component {...(props as P)} location={location}>
        {children}
      </Component>
    );
  };
}

export default withLocation(ApiErrorBoundary);
