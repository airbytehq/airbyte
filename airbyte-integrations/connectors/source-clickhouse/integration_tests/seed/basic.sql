CREATE TABLE IF NOT EXISTS default.id_and_name (id INTEGER, name VARCHAR(200)) ENGINE = TinyLog;
INSERT INTO default.id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');

CREATE TABLE IF NOT EXISTS default.starships (id INTEGER, name VARCHAR(200)) ENGINE = TinyLog;
INSERT INTO default.starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');
