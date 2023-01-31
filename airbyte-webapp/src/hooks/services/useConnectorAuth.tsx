import { useCallback, useMemo, useRef } from "react";
import { useIntl } from "react-intl";
import { useAsyncFn, useEffectOnce, useEvent } from "react-use";

import { ToastType } from "components/ui/Toast";

import { useConfig } from "config";
import { ConnectorDefinitionSpecification, ConnectorSpecification } from "core/domain/connector";
import { DestinationAuthService } from "core/domain/connector/DestinationAuthService";
import { isSourceDefinitionSpecification } from "core/domain/connector/source";
import { SourceAuthService } from "core/domain/connector/SourceAuthService";
import { DestinationOauthConsentRequest, SourceOauthConsentRequest } from "core/request/AirbyteClient";
import { isCommonRequestError } from "core/request/CommonRequestError";
import { useConnectorForm } from "views/Connector/ConnectorForm/connectorFormContext";

import { useAppMonitoringService } from "./AppMonitoringService";
import { useNotificationService } from "./Notification";
import { useCurrentWorkspace } from "./useWorkspace";
import { useDefaultRequestMiddlewares } from "../../services/useDefaultRequestMiddlewares";
import { useQuery } from "../useQuery";

let windowObjectReference: Window | null = null; // global variable

function openWindow(url: string): void {
  if (windowObjectReference == null || windowObjectReference.closed) {
    /* if the pointer to the window object in memory does not exist
       or if such pointer exists but the window was closed */

    const strWindowFeatures = "toolbar=no,menubar=no,width=600,height=700,top=100,left=100";
    windowObjectReference = window.open(url, "name", strWindowFeatures);
    /* then create it. The new window will be created and
       will be brought on top of any other window. */
  } else {
    windowObjectReference.focus();
    /* else the window reference must exist and the window
       is not closed; therefore, we can bring it back on top of any other
       window with the focus() method. There would be no need to re-create
       the window or to reload the referenced resource. */
  }
}

export function useConnectorAuth(): {
  getConsentUrl: (
    connector: ConnectorDefinitionSpecification,
    oAuthInputConfiguration: Record<string, unknown>
  ) => Promise<{
    payload: SourceOauthConsentRequest | DestinationOauthConsentRequest;
    consentUrl: string;
  }>;
  completeOauthRequest: (
    params: SourceOauthConsentRequest | DestinationOauthConsentRequest,
    queryParams: Record<string, unknown>
  ) => Promise<Record<string, unknown>>;
} {
  const { formatMessage } = useIntl();
  const { trackError } = useAppMonitoringService();
  const { workspaceId } = useCurrentWorkspace();
  const { apiUrl, oauthRedirectUrl } = useConfig();
  const notificationService = useNotificationService();
  const { connectorId } = useConnectorForm();

  // TODO: move to separate initFacade and use refs instead
  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  const sourceAuthService = useMemo(
    () => new SourceAuthService(apiUrl, requestAuthMiddleware),
    [apiUrl, requestAuthMiddleware]
  );
  const destinationAuthService = useMemo(
    () => new DestinationAuthService(apiUrl, requestAuthMiddleware),
    [apiUrl, requestAuthMiddleware]
  );

  return {
    getConsentUrl: async (
      connector: ConnectorDefinitionSpecification,
      oAuthInputConfiguration: Record<string, unknown>
    ): Promise<{
      payload: SourceOauthConsentRequest | DestinationOauthConsentRequest;
      consentUrl: string;
    }> => {
      try {
        if (isSourceDefinitionSpecification(connector)) {
          const payload: SourceOauthConsentRequest = {
            workspaceId,
            sourceDefinitionId: ConnectorSpecification.id(connector),
            redirectUrl: `${oauthRedirectUrl}/auth_flow`,
            oAuthInputConfiguration,
            sourceId: connectorId,
          };
          const response = await sourceAuthService.getConsentUrl(payload);

          return { consentUrl: response.consentUrl, payload };
        }
        const payload: DestinationOauthConsentRequest = {
          workspaceId,
          destinationDefinitionId: ConnectorSpecification.id(connector),
          redirectUrl: `${oauthRedirectUrl}/auth_flow`,
          oAuthInputConfiguration,
          destinationId: connectorId,
        };
        const response = await destinationAuthService.getConsentUrl(payload);

        return { consentUrl: response.consentUrl, payload };
      } catch (e) {
        // If this API returns a 404 the OAuth credentials have not been added to the database.
        if (isCommonRequestError(e) && e.status === 404) {
          if (process.env.NODE_ENV === "development") {
            notificationService.registerNotification({
              id: "oauthConnector.credentialsMissing",
              // Since it's dev only we don't need i18n on this string
              text: "OAuth is not enabled for this connector on this environment.",
            });
          } else {
            // Log error to our monitoring, this should never happen and means OAuth credentials
            // where missed
            trackError(e, {
              id: "oauthConnector.credentialsMissing",
              connectorSpecId: ConnectorSpecification.id(connector),
              workspaceId,
            });
            notificationService.registerNotification({
              id: "oauthConnector.credentialsMissing",
              text: formatMessage({ id: "connector.oauthCredentialsMissing" }),
              type: ToastType.ERROR,
            });
          }
        }
        throw e;
      }
    },
    completeOauthRequest: async (
      params: SourceOauthConsentRequest | DestinationOauthConsentRequest,
      queryParams: Record<string, unknown>
    ): Promise<Record<string, unknown>> => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const payload: any = {
        ...params,
        queryParams,
      };
      return (payload as SourceOauthConsentRequest).sourceDefinitionId
        ? sourceAuthService.completeOauth(payload)
        : destinationAuthService.completeOauth(payload);
    },
  };
}

export function useRunOauthFlow(
  connector: ConnectorDefinitionSpecification,
  onDone?: (values: Record<string, unknown>) => void
): {
  loading: boolean;
  done?: boolean;
  run: (oauthInputParams: Record<string, unknown>) => void;
} {
  const { getConsentUrl, completeOauthRequest } = useConnectorAuth();
  const param = useRef<SourceOauthConsentRequest | DestinationOauthConsentRequest>();

  const [{ loading }, onStartOauth] = useAsyncFn(
    async (oauthInputParams: Record<string, unknown>) => {
      const consentRequestInProgress = await getConsentUrl(connector, oauthInputParams);

      param.current = consentRequestInProgress.payload;
      openWindow(consentRequestInProgress.consentUrl);
    },
    [connector]
  );

  const [{ loading: loadingCompleteOauth, value }, completeOauth] = useAsyncFn(
    async (queryParams: Record<string, unknown>) => {
      const oauthStartedPayload = param.current;

      if (oauthStartedPayload) {
        const completeOauthResponse = await completeOauthRequest(oauthStartedPayload, queryParams);

        onDone?.(completeOauthResponse);
        return true;
      }

      return !!oauthStartedPayload;
    },
    [connector, onDone]
  );

  const onOathGranted = useCallback(
    async (event: MessageEvent) => {
      // TODO: check if more secure option is required
      if (
        event.origin === window.origin &&
        // In case of oAuth 1.0a there would be no "state" field
        // but it would be "oauth_verifier" parameter.
        (event.data?.state || event.data?.oauth_verifier)
      ) {
        await completeOauth(event.data);
      }
    },
    [completeOauth]
  );

  const onCloseWindow = useCallback(() => {
    windowObjectReference?.close();
  }, []);

  useEvent("message", onOathGranted);
  // Close popup oauth window when we close the original tab
  useEvent("beforeunload", onCloseWindow);

  return {
    loading: loadingCompleteOauth || loading,
    done: value,
    run: onStartOauth,
  };
}

export function useResolveNavigate(): void {
  const query = useQuery();

  useEffectOnce(() => {
    window.opener?.postMessage(query);
    window.close();
  });
}
