import {
  ConnectorDefinitionSpecification,
  ConnectorSpecification,
} from "core/domain/connector";

import { useCurrentWorkspace } from "./useWorkspace";
import { SourceAuthService } from "core/domain/connector/ConnectorOauthService";
import { useConfig } from "config";
import { useLocalStorage } from "react-use";

export function useConnectorAuth() {
  const [state, setState] = useLocalStorage<object>(`state`, undefined);
  const { workspaceId } = useCurrentWorkspace();
  const { apiUrl } = useConfig();
  const sourceAuth = new SourceAuthService(apiUrl);
  return {
    getConsentUrl: async (connector: ConnectorDefinitionSpecification) => {
      // TODO: add destination logic
      const payload = {
        workspaceId,
        sourceDefinitionId: ConnectorSpecification.id(connector),
        redirectUrl: "http://localhost:3000/auth_flow",
      };

      const response = await sourceAuth.getConsentUrl(payload);

      setState(payload);

      window.open(response.consentUrl);
    },
    completeOauthRequest: async (
      _connector: ConnectorDefinitionSpecification,
      queryParams: any
    ) => {
      console.log(queryParams);
      if (!state) {
        return;
      }
      const response = await sourceAuth.completeOauth({
        ...state,
        queryParams: { code: queryParams.code },
      });

      console.log(response);
    },
  };
}
