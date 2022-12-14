/**
 * Converts Cypress chain to regular Promise.
 */
export const toPromise = <T>(chain: Cypress.Chainable<T>): Promise<T> => {
  return new Cypress.Promise((resolve, reject) => {
    const onFail = (error: Error) => {
      Cypress.off("fail", onFail);
      reject(error);
    };

    Cypress.on("fail", onFail);

    chain.then((value) => {
      Cypress.off("fail", onFail);
      resolve(value);
    });
  });
};
