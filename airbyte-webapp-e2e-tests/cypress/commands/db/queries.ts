export const createTable = (tableName: string, columns: string[]): string =>
  `CREATE TABLE ${tableName}(${columns.join(", ")});`;

export const dropTable = (tableName: string) => `DROP TABLE IF EXISTS ${tableName}`;

export const alterTable = (tableName: string, params: { add?: string[]; drop?: string[] }): string => {
  const adds = params.add ? params.add.map((add) => `ADD COLUMN ${add}`) : [];
  const drops = params.drop ? params.drop.map((columnName) => `DROP COLUMN ${columnName}`) : [];
  const alterations = [...adds, ...drops];

  return `ALTER TABLE ${tableName} ${alterations.join(", ")};`;
};

export const insertIntoTable = (tableName: string, valuesByColumn: Record<string, unknown>): string => {
  const keys = Object.keys(valuesByColumn);
  const values = keys
    .map((key) => valuesByColumn[key])
    .map((value) => (typeof value === "string" ? `'${value}'` : value));

  return `INSERT INTO ${tableName}(${keys.join(", ")}) VALUES(${values.join(", ")});`;
};

export const insertMultipleIntoTable = (tableName: string, valuesByColumns: Array<Record<string, unknown>>): string =>
  valuesByColumns.map((valuesByColumn) => insertIntoTable(tableName, valuesByColumn)).join("\n");

// Users table
export const createUsersTableQuery = createTable("public.users", [
  "id SERIAL",
  "name VARCHAR(200) NULL",
  "email VARCHAR(200) NULL",
  "updated_at TIMESTAMP",
  "CONSTRAINT users_pkey PRIMARY KEY (id)",
]);
export const insertUsersTableQuery = insertMultipleIntoTable("public.users", [
  { name: "Abigail", email: "abigail@example.com", updated_at: "2022-12-19 00:00:00" },
  { name: "Andrew", email: "andrew@example.com", updated_at: "2022-12-19 00:00:00" },
  { name: "Kat", email: "kat@example.com", updated_at: "2022-12-19 00:00:00" },
]);

export const dropUsersTableQuery = dropTable("public.users");

// Cities table
export const createCitiesTableQuery = createTable("public.cities", ["city_code VARCHAR(8)", "city VARCHAR(200)"]);

export const insertCitiesTableQuery = insertMultipleIntoTable("public.cities", [
  {
    city_code: "BCN",
    city: "Barcelona",
  },
  { city_code: "MAD", city: "Madrid" },
  { city_code: "VAL", city: "Valencia" },
]);

export const alterCitiesTableQuery = alterTable("public.cities", {
  add: ["state TEXT", "country TEXT"],
  drop: ["city_code"],
});
export const dropCitiesTableQuery = dropTable("public.cities");

// Cars table
export const createCarsTableQuery = createTable("public.cars", [
  "id SERIAL PRIMARY KEY",
  "mark VARCHAR(200)",
  "model VARCHAR(200)",
  "color VARCHAR(200)",
]);

export const dropCarsTableQuery = dropTable("public.cars");
