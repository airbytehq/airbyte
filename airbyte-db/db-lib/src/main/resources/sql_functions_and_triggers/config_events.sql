/*
the goal of this script is to be able to track each change event for a target table. it achieves this by doing a few things:
1. created a config_event table, where all of the tracked events are stored.
2. defines a generic psql function that saves a copy of the record AFTER the event is completed. This function can be called on any table that has the following 2 columns: id (uuid, non-nullable) and updated_by (uuid, nullable)
3. defines a psql function that takes in a table name as an argument and creates a trigger on that table that calls the function defined #2 on insert, updated, or delete.

usage: to add this tracking ability to a table:
`SELECT create_event_trigger('<table name>');`
`SELECT create_event_trigger('actor');`
*/

-- #1 - create config_event table
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE operation_type AS ENUM ('insert', 'update', 'delete');

CREATE TABLE IF NOT EXISTS config_event
(
    "id"             uuid PRIMARY KEY         DEFAULT uuid_generate_v4(),
    "operation_type" operation_type  NOT NULL,
    "config_type"    varchar(256)    NOT NULL,
    "config_id"      uuid            NOT NULL,
    "result"         jsonb           NULL,
    "created_at"     timestamptz(35) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by"     uuid            NULL
);

CREATE INDEX config_id_idx ON config_event (config_id);
CREATE INDEX config_type_and_id_idx ON config_event (config_type, config_id);

-- #2 - declare function that saves copy of the record after it is modified.
-- WARNING: target table must define the following 2 columns: id (uuid, non-nullable) and updated_by (uuid, nullable)
CREATE OR REPLACE FUNCTION process_config_event() RETURNS TRIGGER AS
$$
DECLARE
    -- functions used in triggers cannot take arguments in the traditional way. they can be passed in via TG_ARGS though.
    configtype varchar(256);
BEGIN
    configtype := TG_ARGV[0];
    /*
    Create a row in config_event to reflect the operation performed on the target table. Make use of the special variable TG_OP to work out the operation.
    */
    IF (TG_OP = 'DELETE') THEN
        -- note: for deletes, we cannot track how did the delete.
        INSERT INTO config_event (operation_type, config_type, config_id, result, created_at, created_by)
        VALUES ('delete', configtype, OLD.id, NULL, NOW(), NULL);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO config_event (operation_type, config_type, config_id, result, created_at, created_by)
        VALUES ('update', configtype, NEW.id, to_jsonb(NEW), NOW(), NEW.updated_by);
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO config_event (operation_type, config_type, config_id, result, created_at, created_by)
        VALUES ('insert', configtype, NEW.id, to_jsonb(NEW), NOW(), NEW.updated_by);
        RETURN NEW;
    END IF;
    RETURN NULL; -- result is ignored since this is an AFTER trigger
END;
$$ LANGUAGE plpgsql;

-- #3 -- declare function that creates a config event trigger for a given table. takes table name as an argument.
CREATE OR REPLACE FUNCTION create_config_event_trigger(text)
    RETURNS void AS
$$
BEGIN
    /*
    psql does not allow interpolation in trigger creation, so need to trick it by creating the desired string with interpolation and then calling EXECUTE. See in comment below the command transcribed in vanilla SQL. The statement below is the equivalent of

    CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON <tablename>
    FOR EACH ROW
    EXECUTE PROCEDURE updated_at_timestamp_trigger_function();
    */
    EXECUTE (FORMAT(
            'CREATE TRIGGER config_event_trigger AFTER INSERT OR UPDATE OR DELETE ON %s FOR EACH ROW EXECUTE PROCEDURE process_config_event(%s);',
            $1,
            $1));
END;
$$ LANGUAGE plpgsql;
