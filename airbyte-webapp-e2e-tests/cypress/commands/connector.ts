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
} from "pages/createConnectorPage";

export const fillPostgresForm = (
  name: string,
  host: string,
  port: string,
  database: string,
  username: string,
  password: string
) => {
  cy.intercept("/api/v1/source_definition_specifications/get").as("getSourceSpecifications");

  selectServiceType("Postgres");

  cy.wait("@getSourceSpecifications");

  enterName(name);
  enterHost(host);
  enterPort(port);
  enterDatabase(database);
  enterUsername(username);
  enterPassword(password);
};

export const fillPokeAPIForm = (name: string, pokeName: string) => {
  cy.intercept("/api/v1/source_definition_specifications/get").as("getSourceSpecifications");

  selectServiceType("PokeAPI");

  cy.wait("@getSourceSpecifications");

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
