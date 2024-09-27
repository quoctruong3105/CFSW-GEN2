-- Global user and role setup
CREATE USER svcfsw WITH ENCRYPTED PASSWORD 'cfsw12345';
ALTER USER svcfsw WITH SUPERUSER;
ALTER USER postgres WITH PASSWORD 'cfsw12345';

------------------------------------------------
-- Init database for account service
------------------------------------------------
CREATE DATABASE "account";

\c "account"

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

\c "order"

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

\c "authorize"

CREATE TABLE IF NOT EXISTS authorize_keys
(
    key text
);
