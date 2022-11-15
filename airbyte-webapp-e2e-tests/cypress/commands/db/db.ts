import {
  createCitiesTableQuery,
  createUsersTableQuery,
  insertCitiesTableQuery,
  insertUsersTableQuery,
} from "./queries";

/**
 * Launch docker Postgres instance
 */
const createDB = () => cy.exec("npm run createdb");

/**
 * Wrapper for DB Query Cypress task
 * @param queryString
 */
export const runDbQuery = <T>(queryString: string) => cy.task<T>("dbQuery", { query: queryString });

interface TableExistsResponse {
  exists: boolean;
}
/**
 * Function for composing the query for checking the existence of a table
 * @param tableName
 * @return string
 */
const composeIsTableExistQuery = (tableName: string) =>
  `SELECT EXISTS (SELECT FROM pg_tables
		WHERE
        schemaname = 'public' AND
        tablename  = '${tableName}'
      )`;

// Users table
interface User {
  id: number;
  col1: string;
}

export const populateUsersTable = () => {
  runDbQuery<TableExistsResponse[]>(composeIsTableExistQuery("users")).then((results) => {
    const [{ exists }] = results;
    if (exists) {
      return;
    }

    runDbQuery(createUsersTableQuery).then(() => {
      runDbQuery(insertUsersTableQuery).then(() => {
        runDbQuery<User[]>("SELECT * FROM users").then((results) => {
          // just to make sure the table is populated
          expect(results[0].id).to.equal(1);
          expect(results[2].col1).to.equal("record3");
        });
      });
    });
  });
};

// Cities table
interface City {
  city_code: string;
  city: string;
}

export const populateCitiesTable = () => {
  runDbQuery<TableExistsResponse[]>(composeIsTableExistQuery("cities")).then((results) => {
    const [{ exists }] = results;
    if (exists) {
      return;
    }

    runDbQuery(createCitiesTableQuery).then(() => {
      runDbQuery(insertCitiesTableQuery).then(() => {
        runDbQuery<City[]>("SELECT * FROM cities").then((results) => {
          // just to make sure the table is populated
          expect(results[0].city_code).to.equal("BCN");
          expect(results[2].city).to.equal("Valencia");
        });
      });
    });
  });
};

export const PopulatePostgresDBSource = () => {
  populateUsersTable();
  populateCitiesTable();
};
