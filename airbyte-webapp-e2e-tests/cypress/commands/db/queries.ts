// Users table
export const createUsersTableQuery = `
    CREATE TABLE users(id SERIAL PRIMARY KEY, col1 VARCHAR(200));`;
export const insertUsersTableQuery = `
    INSERT INTO public.users(col1) VALUES('record1');
    INSERT INTO public.users(col1) VALUES('record2');
    INSERT INTO public.users(col1) VALUES('record3');`;

// Cities table
export const createCitiesTableQuery = `
    CREATE TABLE cities(city_code VARCHAR(8), city VARCHAR(200));`;

export const insertCitiesTableQuery = `
    INSERT INTO public.cities(city_code, city) VALUES('BCN', 'Barcelona');
    INSERT INTO public.cities(city_code, city) VALUES('MAD', 'Madrid');
    INSERT INTO public.cities(city_code, city) VALUES('VAL', 'Valencia')`;
