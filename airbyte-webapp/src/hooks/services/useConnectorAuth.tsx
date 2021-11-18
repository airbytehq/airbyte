import { useFormikContext } from "formik";
import { useCallback, useMemo, useRef } from "react";
import { useAsyncFn, useEffectOnce, useEvent } from "react-use";
import merge from "lodash.merge";

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

export function useConnectorAuth() {
  const { workspaceId } = useCurrentWorkspace();
  const { apiUrl, oauthRedirectUrl } = useConfig();
  const middlewares = useGetService<RequestMiddleware[]>(
    "DefaultRequestMiddlewares"
  );

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
      connector: ConnectorDefinitionSpecification
    ): Promise<{
      payload: SourceGetConsentPayload | DestinationGetConsentPayload;
      consentUrl: string;
    }> => {
      if (isSourceDefinitionSpecification(connector)) {
        const payload = {
          workspaceId,
          sourceDefinitionId: ConnectorSpecification.id(connector),
          redirectUrl: `${oauthRedirectUrl}/auth_flow`,
        };
        const response = await sourceAuthService.getConsentUrl(payload);

        return { consentUrl: response.consentUrl, payload };
      } else {
        const payload = {
          workspaceId,
          destinationDefinitionId: ConnectorSpecification.id(connector),
          redirectUrl: `${oauthRedirectUrl}/auth_flow`,
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
  connector: ConnectorDefinitionSpecification
): {
  loading: boolean;
  done?: boolean;
  run: () => void;
} {
  const { values, setValues } = useFormikContext();
  const { getConsentUrl, completeOauthRequest } = useConnectorAuth();
  const param = useRef<
    SourceGetConsentPayload | DestinationGetConsentPayload
  >();

  const [{ loading }, onStartOauth] = useAsyncFn(async () => {
    const consentRequestInProgress = await getConsentUrl(connector);

    param.current = consentRequestInProgress.payload;
    openWindow(consentRequestInProgress.consentUrl);
  }, [connector]);

  const [{ loading: loadingCompleteOauth, value }, completeOauth] = useAsyncFn(
    async (queryParams: Record<string, unknown>) => {
      const oauthStartedPayload = param.current;

      if (oauthStartedPayload) {
        const connectionConfiguration = await completeOauthRequest(
          oauthStartedPayload,
          queryParams
        );

        setValues(merge(values, { connectionConfiguration }));
        return true;
      }

      return false;
    },
    [connector, values]
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

export function useResolveRedirect(): void {
  const { query } = useRouter();

  useEffectOnce(() => {
    window.opener.postMessage(query);
    window.close();
  });
}
