import { toPromise } from "./utils/promise";

let _workspaceId: string;

const getApiUrl = (path: string): string => `http://localhost:8001/api/v1${path}`;

export const getPostgresCreateSourceBody = (name: string) => ({
  name,
  sourceDefinitionId: "decd338e-5647-4c0b-adf4-da0e75f5a750",
  workspaceId: _workspaceId,
  connectionConfiguration: {
    ssl_mode: { mode: "disable" },
    tunnel_method: { tunnel_method: "NO_TUNNEL" },
    replication_method: { method: "Standard" },
    ssl: false,
    port: 5433,
    schemas: ["public"],
    host: "localhost",
    database: "airbyte_ci_source",
    username: "postgres",
    password: "secret_password",
  },
});

export const requestWorkspaceId = () => {
  if (!_workspaceId) {
    cy.request("POST", getApiUrl("/workspaces/list")).then((response) => {
      expect(response.status).to.eq(200);
      ({
        workspaces: [{ workspaceId: _workspaceId }],
      } = response.body);
    });
  }
};

const apiRequest = <T = void>(
  method: Cypress.HttpMethod,
  path: string,
  payload: Record<string, unknown> | undefined,
  expectedStatus: number
): Promise<T> =>
  toPromise<T>(
    cy.request(method, getApiUrl(path), payload).then((response) => {
      expect(response.status).to.eq(expectedStatus, "response status");
      return response.body;
    })
  );

export const requestCreateSource = (name: string, payload: Record<string, unknown>) =>
  apiRequest<{ sourceId: string }>("POST", "/sources/create", payload, 200);

export const requestDeleteSource = (sourceId: string) => apiRequest("POST", "/sources/delete", { sourceId }, 204);

export const requestCreateDestination = (name: string, payload: Record<string, unknown>) =>
  apiRequest<{ destinationId: string }>("POST", "/destinations/create", payload, 200);

export const requestDeleteDestination = (destinationId: string) =>
  apiRequest("POST", "/destinations/delete", { destinationId }, 204);
