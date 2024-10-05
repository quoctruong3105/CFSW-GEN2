------------------------------------------------
-- Init database for account service
------------------------------------------------
CREATE DATABASE "account";

\c "account"

CREATE TABLE ACCOUNT (
    account_id SERIAL PRIMARY KEY,
    username VARCHAR(25) NOT NULL UNIQUE,
    password VARCHAR(25) NOT NULL,
    role VARCHAR(10) NOT NULL,
    last_login TIMESTAMP,
    last_logout TIMESTAMP
);

-- INSERT INTO ACCOUNT (username, password, role, last_login, last_logout)
-- VALUES
--     ('john_doe', '12345', 'admin','2024-09-18 09:00:00', '2024-09-18 17:00:00'),
--     ('jane_smith', '67890', 'cashier', '2024-09-18 08:30:00', '2024-09-18 16:30:00'),
--     ('alice_wong', 'AlicePassword', 'CEO', NULL, NULL);
