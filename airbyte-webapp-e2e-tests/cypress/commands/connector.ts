import {
  enterDestinationPath,
  selectServiceType,
  enterName,
  enterHost,
  enterPort,
  enterDatabase,
  enterUsername,
  enterPassword,
  enterPokemonName,
  enterSchema,
} from "pages/createConnectorPage";

export const fillPostgresForm = (
  name: string,
  host: string,
  port: string,
  database: string,
  username: string,
  password: string,
  schema: string
) => {
  cy.intercept("/api/v1/source_definition_specifications/get").as("getSourceSpecifications");

  selectServiceType("Postgres");

  enterName(name);
  enterHost(host);
  enterPort(port);
  enterDatabase(database);
  enterSchema(schema);
  enterUsername(username);
  enterPassword(password);
};

export const fillPokeAPIForm = (name: string, pokeName: string) => {
  cy.intercept("/api/v1/source_definition_specifications/get").as("getSourceSpecifications");

  selectServiceType("PokeAPI");

  enterName(name);
  enterPokemonName(pokeName);
};

export const fillLocalJsonForm = (name: string, destinationPath: string) => {
  cy.intercept("/api/v1/destination_definition_specifications/get").as("getDestinationSpecifications");

  selectServiceType("Local JSON");

  cy.wait("@getDestinationSpecifications");

  enterName(name);
  enterDestinationPath(destinationPath);
};
