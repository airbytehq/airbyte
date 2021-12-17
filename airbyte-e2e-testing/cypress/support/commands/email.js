const { MailSlurp } = require("mailslurp-client");

const apiKey =
  "caf2ce54b4c3f71bf459491e36c256cdb4662e5a80307f75e63cb560ab8ace28";
const mailslurp = new MailSlurp({ apiKey });

Cypress.on("uncaught:exception", (err, runnable) => {
  return false;
});

Cypress.Commands.add("forceVisit", (url) => {
  cy.window().then((win) => {
    return win.open(url, "_self");
  });
});

Cypress.Commands.add("clearApp", (url) => {
  indexedDB.deleteDatabase("firebaseLocalStorageDb");
  cy.clearLocalStorage();
  cy.clearCookies();
});

Cypress.Commands.add("createInbox", () => {
  return mailslurp.createInbox();
});

Cypress.Commands.add("waitForLatestEmail", (inboxId) => {
  return mailslurp.waitForLatestEmail(inboxId);
});

Cypress.Commands.add("openSettings", () => {
  cy.get("a[data-testid='sidebar.settings']").click();
});
