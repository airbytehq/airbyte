// Users table
export const createUsersTableQuery = `
    CREATE TABLE users(id SERIAL PRIMARY KEY, col1 VARCHAR(200));`;
export const insertUsersTableQuery = `
    INSERT INTO public.users(col1) VALUES('record1');
    INSERT INTO public.users(col1) VALUES('record2');
    INSERT INTO public.users(col1) VALUES('record3');`;

export const dropUsersTableQuery = `
    DROP TABLE IF EXISTS users;`;

// Cities table
export const createCitiesTableQuery = `
    CREATE TABLE cities(city_code VARCHAR(8), city VARCHAR(200));`;

export const insertCitiesTableQuery = `
    INSERT INTO public.cities(city_code, city) VALUES('BCN', 'Barcelona');
    INSERT INTO public.cities(city_code, city) VALUES('MAD', 'Madrid');
    INSERT INTO public.cities(city_code, city) VALUES('VAL', 'Valencia')`;

export const alterCitiesTableQuery = `
    ALTER TABLE public.cities 
    DROP COLUMN "city_code",
    ADD COLUMN "state" text,
    ADD COLUMN "country" text;`;
export const dropCitiesTableQuery = `
    DROP TABLE IF EXISTS cities;`;

// Cars table
export const createCarsTableQuery = `
    CREATE TABLE cars(id SERIAL PRIMARY KEY, mark VARCHAR(200), model VARCHAR(200), color VARCHAR(200));`;
export const dropCarsTableQuery = `
    DROP TABLE IF EXISTS cars;`;
