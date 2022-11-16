import { Suspense } from "react";
import React from "react";
import { FormattedMessage } from "react-intl";
import { Navigate, useNavigate } from "react-router-dom";

import { LoadingPage } from "components/LoadingPage";

import { useConfig } from "config";
import { getSpeakeasyCallbackUrl } from "core/request/CloudApiClient";
import { useAppMonitoringService } from "hooks/services/AppMonitoringService";
import { RoutePaths } from "pages/routePaths";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { ErrorOccurredView } from "views/common/ErrorOccurredView";

const SPEAKEASY_QUERY_KEY = "speakeasy-redirect";

export const SpeakeasyRedirectPage = () => {
  const { trackError } = useAppMonitoringService();

  return (
    <SpeakeasyErrorBoundary trackError={trackError}>
      <SpeakeasyLoginRedirect />
    </SpeakeasyErrorBoundary>
  );
};

const SpeakeasyLoginRedirect = () => {
  const { apiUrl } = useConfig();
  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  const { redirectUrl } = useSuspenseQuery(SPEAKEASY_QUERY_KEY, () =>
    getSpeakeasyCallbackUrl({ config: { apiUrl }, middlewares: requestAuthMiddleware })
  );

  return (
    <Suspense fallback={<LoadingPage />}>
      {redirectUrl ? <Navigate to={redirectUrl} /> : <CloudApiErrorView />}
    </Suspense>
  );
};

const CloudApiErrorView = () => {
  const navigate = useNavigate();
  return (
    <ErrorOccurredView
      message={<FormattedMessage id="cloudApi.loginCallbackUrlError" />}
      ctaButtonText={<FormattedMessage id="ui.goBack" />}
      onCtaButtonClick={() => {
        navigate(RoutePaths.Root);
      }}
    />
  );
};

interface SpeakeasyErrorBoundaryProps {
  trackError: (e: Error, context?: Record<string, unknown>) => void;
}

export class SpeakeasyErrorBoundary extends React.Component<React.PropsWithChildren<SpeakeasyErrorBoundaryProps>> {
  state = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error): void {
    this.props.trackError(error);
  }

  render() {
    if (this.state.error) {
      return <CloudApiErrorView />;
    }
    return this.props.children;
  }
}
