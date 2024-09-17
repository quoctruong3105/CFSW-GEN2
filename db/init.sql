CREATE USER svcfsw WITH ENCRYPTED PASSWORD 'cfsw12345';

-----------------------------------------------
-- Init database for account service          
-----------------------------------------------
CREATE DATABASE account;
GRANT ALL PRIVILEGES ON DATABASE account TO svcfsw;
\connect account
CREATE TABLE IF NOT EXISTS accounts
(
    id serial PRIMARY KEY,
    username varchar(255) NOT NULL,
    password varchar(255) NOT NULL,
    last_login text,
    last_logout text
)

-----------------------------------------------
-- Init database for order service
-----------------------------------------------
CREATE DATABASE order;
GRANT ALL PRIVILEGES ON DATABASE order TO svcfsw;
\connect order
CREATE TABLE IF NOT EXISTS banks
(
    acqid text,
    accountno text,
    accountname text
)
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
)

-----------------------------------------------
-- Init database for license service
-----------------------------------------------
CREATE DATABASE license;
GRANT ALL PRIVILEGES ON DATABASE license TO svcfsw;
\connect license
CREATE TABLE IF NOT EXISTS license_keys
(
    key text
)
