import {
  ConnectionGetBody,
  Connection,
  ConnectionCreateRequestBody,
  ConnectionsList,
  Destination,
  DestinationsList,
  Source,
  SourceDiscoverSchema,
  SourcesList,
} from "./types";
import { getWorkspaceId, setWorkspaceId } from "./workspace";

const getApiUrl = (path: string): string => `http://localhost:8001/api/v1${path}`;

const apiRequest = <T = void>(
  method: Cypress.HttpMethod,
  path: string,
  payload?: Cypress.RequestBody,
  expectedStatus = 200
): Cypress.Chainable<T> =>
  cy.request(method, getApiUrl(path), payload).then((response) => {
    expect(response.status).to.eq(expectedStatus, "response status");
    return response.body;
  });

export const requestWorkspaceId = () =>
  apiRequest<{ workspaces: Array<{ workspaceId: string }> }>("POST", "/workspaces/list").then(
    ({ workspaces: [{ workspaceId }] }) => {
      setWorkspaceId(workspaceId);
    }
  );

export const requestConnectionsList = () =>
  apiRequest<ConnectionsList>("POST", "/connections/list", { workspaceId: getWorkspaceId() });

export const requestCreateConnection = (body: ConnectionCreateRequestBody) =>
  apiRequest<Connection>("POST", "/web_backend/connections/create", body);

export const requestUpdateConnection = (body: Record<string, unknown>) =>
  apiRequest<Connection>("POST", "/web_backend/connections/update", body);

export const requestGetConnection = (body: ConnectionGetBody) =>
  apiRequest<Connection>("POST", "/web_backend/connections/get", body);

export const requestDeleteConnection = (connectionId: string) =>
  apiRequest("POST", "/connections/delete", { connectionId }, 204);

export const requestSourcesList = () =>
  apiRequest<SourcesList>("POST", "/sources/list", { workspaceId: getWorkspaceId() });

export const requestSourceDiscoverSchema = (sourceId: string) =>
  apiRequest<SourceDiscoverSchema>("POST", "/sources/discover_schema", { sourceId, disable_cache: true });

export const requestCreateSource = (body: Record<string, unknown>) =>
  apiRequest<Source>("POST", "/sources/create", body);

export const requestDeleteSource = (sourceId: string) => apiRequest("POST", "/sources/delete", { sourceId }, 204);

export const requestDestinationsList = () =>
  apiRequest<DestinationsList>("POST", "/destinations/list", { workspaceId: getWorkspaceId() });

export const requestCreateDestination = (body: Record<string, unknown>) =>
  apiRequest<Destination>("POST", "/destinations/create", body);

export const requestDeleteDestination = (destinationId: string) =>
  apiRequest("POST", "/destinations/delete", { destinationId }, 204);
