import { Suspense, useEffect } from "react";
import React from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { LoadingPage } from "components/LoadingPage";

import { useAppMonitoringService, TrackErrorFn } from "hooks/services/AppMonitoringService";
import { useSpeakeasyRedirect } from "packages/cloud/services/speakeasy";
import { RoutePaths } from "pages/routePaths";
import { ErrorOccurredView } from "views/common/ErrorOccurredView";

export const SpeakeasyRedirectPage = () => {
  const { trackError } = useAppMonitoringService();

  return (
    <SpeakeasyErrorBoundary trackError={trackError}>
      <Suspense fallback={<LoadingPage />}>
        <SpeakeasyLoginRedirect />
      </Suspense>
    </SpeakeasyErrorBoundary>
  );
};

const SpeakeasyLoginRedirect = () => {
  const { redirectUrl } = useSpeakeasyRedirect();

  useEffect(() => {
    if (redirectUrl) {
      window.location.replace(redirectUrl);
    }
  }, [redirectUrl]);

  return redirectUrl ? <LoadingPage /> : <CloudApiErrorView />;
};

const CloudApiErrorView = () => {
  const navigate = useNavigate();
  return (
    <ErrorOccurredView
      message={<FormattedMessage id="cloudApi.loginCallbackUrlError" />}
      ctaButtonText={<FormattedMessage id="ui.goToHome" />}
      onCtaButtonClick={() => {
        navigate(RoutePaths.Root);
      }}
    />
  );
};

interface SpeakeasyErrorBoundaryProps {
  trackError: TrackErrorFn;
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
