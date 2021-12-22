import { useCallback, useMemo, useRef } from "react";
import { useAsyncFn, useEffectOnce, useEvent } from "react-use";

import {
  ConnectorDefinitionSpecification,
  ConnectorSpecification,
  DestinationGetConsentPayload,
  SourceGetConsentPayload,
} from "core/domain/connector";

import { useConfig } from "config";
import { useCurrentWorkspace } from "./useWorkspace";
import { SourceAuthService } from "core/domain/connector/SourceAuthService";
import { DestinationAuthService } from "core/domain/connector/DestinationAuthService";
import { useGetService } from "core/servicesProvider";
import { RequestMiddleware } from "core/request/RequestMiddleware";
import { isSourceDefinitionSpecification } from "core/domain/connector/source";
import useRouter from "../useRouter";

let windowObjectReference: Window | null = null; // global variable

function openWindow(url: string): void {
  if (windowObjectReference == null || windowObjectReference.closed) {
    /* if the pointer to the window object in memory does not exist
       or if such pointer exists but the window was closed */

    const strWindowFeatures =
      "toolbar=no,menubar=no,width=600,height=700,top=100,left=100";
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
    payload: SourceGetConsentPayload | DestinationGetConsentPayload;
    consentUrl: string;
  }>;
  completeOauthRequest: (
    params: SourceGetConsentPayload | DestinationGetConsentPayload,
    queryParams: Record<string, unknown>
  ) => Promise<Record<string, unknown>>;
} {
  const { workspaceId } = useCurrentWorkspace();
  const { apiUrl, oauthRedirectUrl } = useConfig();
  const middlewares = useGetService<RequestMiddleware[]>(
    "DefaultRequestMiddlewares"
  );

  // TODO: move to separate initFacade and use refs instead
  const sourceAuthService = useMemo(
    () => new SourceAuthService(apiUrl, middlewares),
    [apiUrl, middlewares]
  );
  const destinationAuthService = useMemo(
    () => new DestinationAuthService(apiUrl, middlewares),
    [apiUrl, middlewares]
  );

  return {
    getConsentUrl: async (
      connector: ConnectorDefinitionSpecification,
      oAuthInputConfiguration: Record<string, unknown>
    ): Promise<{
      payload: SourceGetConsentPayload | DestinationGetConsentPayload;
      consentUrl: string;
    }> => {
      if (isSourceDefinitionSpecification(connector)) {
        const payload = {
          workspaceId,
          sourceDefinitionId: ConnectorSpecification.id(connector),
          redirectUrl: `${oauthRedirectUrl}/auth_flow`,
          oAuthInputConfiguration,
        };
        const response = await sourceAuthService.getConsentUrl(payload);

        return { consentUrl: response.consentUrl, payload };
      } else {
        const payload = {
          workspaceId,
          destinationDefinitionId: ConnectorSpecification.id(connector),
          redirectUrl: `${oauthRedirectUrl}/auth_flow`,
          oAuthInputConfiguration,
        };
        const response = await destinationAuthService.getConsentUrl(payload);

        return { consentUrl: response.consentUrl, payload };
      }
    },
    completeOauthRequest: async (
      params: SourceGetConsentPayload | DestinationGetConsentPayload,
      queryParams: Record<string, unknown>
    ): Promise<Record<string, unknown>> => {
      const payload: any = {
        ...params,
        queryParams,
      };
      return (payload as SourceGetConsentPayload).sourceDefinitionId
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
  const param = useRef<
    SourceGetConsentPayload | DestinationGetConsentPayload
  >();

  const [{ loading }, onStartOauth] = useAsyncFn(
    async (oauthInputParams: Record<string, unknown>) => {
      const consentRequestInProgress = await getConsentUrl(
        connector,
        oauthInputParams
      );

      param.current = consentRequestInProgress.payload;
      openWindow(consentRequestInProgress.consentUrl);
    },
    [connector]
  );

  const [{ loading: loadingCompleteOauth, value }, completeOauth] = useAsyncFn(
    async (queryParams: Record<string, unknown>) => {
      const oauthStartedPayload = param.current;

      if (oauthStartedPayload) {
        const completeOauthResponse = await completeOauthRequest(
          oauthStartedPayload,
          queryParams
        );

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

  useEvent("message", onOathGranted);

  return {
    loading: loadingCompleteOauth || loading,
    done: value,
    run: onStartOauth,
  };
}

export function useResolveNavigate(): void {
  const { query } = useRouter();

  useEffectOnce(() => {
    window.opener.postMessage(query);
    window.close();
  });
}
