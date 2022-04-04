declare global {
  namespace Cypress {
    interface Chainable {
      clearApp(): Chainable<Element>;

      // sidebar

      openSettings(): Chainable<Element>;
    }
  }
}
