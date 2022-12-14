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

export const requestCreateSource = (name: string, payload: Record<string, unknown>) => {
  return cy.request("POST", getApiUrl("/sources/create"), payload).then((response) => {
    expect(response.status).to.eq(200);

    return response.body as { sourceId: string };
  });
};

export const requestDeleteSource = (sourceId: string) => {
  return cy.request("POST", getApiUrl("/sources/delete"), { sourceId }).then((response) => {
    expect(response.status).to.eq(204);
  });
};

export const requestCreateDestination = (name: string, payload: Record<string, unknown>) => {
  return cy.request("POST", getApiUrl("/destinations/create"), payload).then((response) => {
    expect(response.status).to.eq(200);

    return response.body as { destinationId: string };
  });
};

export const requestDeleteDestination = (destinationId: string) => {
  return cy.request("POST", getApiUrl("/destinations/delete"), { destinationId }).then((response) => {
    expect(response.status).to.eq(204);
  });
};
