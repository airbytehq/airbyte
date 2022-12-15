import {
  alterCitiesTableQuery,
  createCarsTableQuery,
  createCitiesTableQuery,
  createUsersTableQuery,
  dropCarsTableQuery,
  dropCitiesTableQuery,
  dropUsersTableQuery,
  insertCitiesTableQuery,
  insertUsersTableQuery,
} from "./queries";

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

export const populateDBSource = () => {
  runDbQuery(createUsersTableQuery);
  runDbQuery(insertUsersTableQuery);
  runDbQuery(createCitiesTableQuery);
  runDbQuery(insertCitiesTableQuery);
};

export const makeChangesInDBSource = () => {
  runDbQuery(dropUsersTableQuery);
  runDbQuery(alterCitiesTableQuery);
  runDbQuery(createCarsTableQuery);
};

export const cleanDBSource = () => {
  runDbQuery(dropUsersTableQuery);
  runDbQuery(dropCitiesTableQuery);
  runDbQuery(dropCarsTableQuery);
};
