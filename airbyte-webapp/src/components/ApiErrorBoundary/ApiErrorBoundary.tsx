import React from "react";

import { FormattedMessage } from "react-intl";
import { isVersionError } from "core/request/VersionError";
import { ErrorOccurredView } from "views/common/ErrorOccurredView";

type BoundaryState = { errorId?: string; message?: string };

enum ErrorId {
  VersionMismatch = "version.mismatch",
  ServerUnavailable = "server.unavailable",
}

class ApiErrorBoundary extends React.Component<unknown, BoundaryState> {
  constructor(props: Record<string, unknown>) {
    super(props);
    this.state = {};
  }

  static getDerivedStateFromError(error: {
    message: string;
    status?: number;
    __type?: string;
  }): BoundaryState {
    // Update state so the next render will show the fallback UI.
    if (isVersionError(error)) {
      return { errorId: ErrorId.VersionMismatch, message: error.message };
    }

    const isNetworkBoundaryMessage = error.message === "Failed to fetch";
    const is502 = error.status === 502;

    if (isNetworkBoundaryMessage || is502) {
      return { errorId: ErrorId.ServerUnavailable };
    }

    return {};
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  componentDidCatch(): void {}

  render(): React.ReactNode {
    if (this.state.errorId === ErrorId.VersionMismatch) {
      return <ErrorOccurredView message={this.state.message} />;
    }

    if (this.state.errorId === ErrorId.ServerUnavailable) {
      return (
        <ErrorOccurredView
          message={<FormattedMessage id="webapp.cannotReachServer" />}
        />
      );
    }

    return !this.state.errorId ? this.props.children : "Unknown error occured";
  }
}

export default ApiErrorBoundary;
