import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

// import { Button } from "components/base";

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
          {this.props.onReset && (
            <RetryContainer>
              <button
                onClick={() => {
                  this.setState({ wasReset: true, errorId: undefined }, () => onReset?.());
                }}
              >
                Retry
              </button>
            </RetryContainer>
          )}
        </ErrorOccurredView>
      );
    }

    return !errorId ? (
      <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>{children}</ResourceNotFoundErrorBoundary>
    ) : (
      <ErrorOccurredView message="Unknown error occurred" />
    );
  }
}

export default ApiErrorBoundary;
