const selectTypeDropdown = "div[data-testid='serviceType']";
const getServiceTypeDropdownOption = (serviceName: string) => `div[data-testid='${serviceName}']`;
const nameInput = "input[name=name]";
const hostInput = "input[name='connectionConfiguration.host']";
const portInput = "input[name='connectionConfiguration.port']";
const databaseInput = "input[name='connectionConfiguration.database']";
const usernameInput = "input[name='connectionConfiguration.username']";
const passwordInput = "input[name='connectionConfiguration.password']";
const pokemonNameInput = "input[name='connectionConfiguration.pokemon_name']";
const schemaInput = "[data-testid='tag-input'] input";
const destinationPathInput = "input[name='connectionConfiguration.destination_path']";

export const selectServiceType = (type: string) =>
  cy
    .get(selectTypeDropdown)
    .click()
    .within(() => cy.get(getServiceTypeDropdownOption(type)).click());

export const enterName = (name: string) => {
  cy.get(nameInput).clear().type(name);
};

export const enterHost = (host: string) => {
  cy.get(hostInput).type(host);
};

export const enterPort = (port: string) => {
  cy.get(portInput).type("{selectAll}{del}").type(port);
};

export const enterDatabase = (database: string) => {
  cy.get(databaseInput).type(database);
};

export const enterUsername = (username: string) => {
  cy.get(usernameInput).type(username);
};

export const enterPassword = (password: string) => {
  cy.get(passwordInput).type(password);
};

export const enterPokemonName = (pokeName: string) => {
  cy.get(pokemonNameInput).type(pokeName);
};

export const enterDestinationPath = (destinationPath: string) => {
  cy.get(destinationPathInput).type(destinationPath);
};

export const enterSchema = (value: string) => {
  if (!value) {
    return;
  }
  cy.get(schemaInput).first().type(value, { force: true }).type("{enter}", { force: true });
};

export const removeSchema = (value = "Remove public") => {
  if (!value) {
    return;
  }
  cy.get(`[aria-label*="${value}"]`).click();
};
