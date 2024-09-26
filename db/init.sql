-- Global user and role setup
CREATE USER svcfsw WITH ENCRYPTED PASSWORD 'cfsw12345';

------------------------------------------------
-- Init database for account service
------------------------------------------------
CREATE DATABASE "account";
GRANT ALL PRIVILEGES ON DATABASE "account" TO svcfsw;

\c "account"

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO svcfsw;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO svcfsw;

CREATE TABLE IF NOT EXISTS accounts
(
    id serial PRIMARY KEY,
    username varchar(255) NOT NULL,
    password varchar(255) NOT NULL,
    role varchar(25) NOT NULL,
    last_login text,
    last_logout text
);

INSERT INTO accounts (username, password, role, last_login, last_logout)
VALUES
    ('john_doe', '12345', 'admin','2024-09-18 09:00:00', '2024-09-18 17:00:00'),
    ('jane_smith', '67890', 'cashier', '2024-09-18 08:30:00', '2024-09-18 16:30:00'),
    ('alice_wong', 'AlicePassword', 'CEO' ,NULL, NULL);

------------------------------------------------
-- Init database for order service
------------------------------------------------
CREATE DATABASE "order";
GRANT ALL PRIVILEGES ON DATABASE "order" TO svcfsw;

\c "order"

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO svcfsw;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO svcfsw;

CREATE TABLE IF NOT EXISTS banks
(
    acqid text,
    accountno text,
    accountname text
);

CREATE TABLE IF NOT EXISTS bills
(
    receipt_id varchar(255),
    date_time timestamp without time zone,
    cashier varchar(255),
    items json,
    grand_total integer,
    cash_receive integer,
    cash_change integer,
    is_cash boolean
);

------------------------------------------------
-- Init database for authorize service
------------------------------------------------
CREATE DATABASE "authorize";
GRANT ALL PRIVILEGES ON DATABASE "authorize" TO svcfsw;

\c "authorize"

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO svcfsw;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO svcfsw;

CREATE TABLE IF NOT EXISTS authorize_keys
(
    key text
);
