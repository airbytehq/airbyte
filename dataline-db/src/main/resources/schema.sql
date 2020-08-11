CREATE TABLE DATALINE_METADATA (id varchar(255), value varchar(255), PRIMARY KEY (id));
INSERT INTO DATALINE_METADATA VALUES  ('server-uuid', ((lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6))))));
CREATE TABLE JOBS (id INTEGER, connection_id varchar(255), created_at INTEGER, started_at INTEGER, updated_at INTEGER, status INTEGER);
CREATE TABLE JOB_ATTEMPTS (id INTEGER, job_id INTEGER, created_at INTEGER, started_at INTEGER, updated_at INTEGER, last_heartbeat INTEGER, status INTEGER, stdout_path varchar(255), stderr_path varchar(255));
