import React from "react";
import { FormattedMessage } from "react-intl";

import { CommonRequestError } from "core/request/CommonRequestError";

interface BoundaryState {
  hasError: boolean;
  message?: React.ReactNode | null;
}

const initialState: BoundaryState = {
  hasError: false,
  message: null,
};

export class ResourceNotFoundErrorBoundary extends React.Component<
  React.PropsWithChildren<{ errorComponent: React.ReactElement }>,
  BoundaryState
> {
  static getDerivedStateFromError(error: CommonRequestError): BoundaryState {
    if (error.status && [401, 404, 422].includes(error.status)) {
      const messageId = error.status === 401 ? "errorView.notAuthorized" : "errorView.notFound";
      return {
        hasError: true,
        message: <FormattedMessage id={messageId} />,
      };
    }
    throw error;
  }

  state = initialState;

  reset = (): void => {
    this.setState(initialState);
  };

  render(): React.ReactNode {
    return this.state.hasError
      ? React.cloneElement(this.props.errorComponent, {
          message: this.state.message,
          onReset: this.reset,
        })
      : this.props.children;
  }
}
