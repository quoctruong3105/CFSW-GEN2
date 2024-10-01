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
    account_id SERIAL PRIMARY KEY,
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
    ('alice_wong', 'AlicePassword', 'CEO', NULL, NULL);

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

------------------------------------------------
-- Init database for inventory service
------------------------------------------------
CREATE DATABASE "inventory";

\c "inventory"

CREATE TABLE DRINK_GROUP (
    drink_group_id SERIAL PRIMARY KEY,
    drink_group VARCHAR(255)
);

CREATE TABLE DRINK (
    drink_id SERIAL PRIMARY KEY,
    drink VARCHAR(255),
    m_cost DECIMAL(10, 2),
    l_cost DECIMAL(10, 2),
    drink_group_id INT,
    FOREIGN KEY (drink_group_id) REFERENCES DRINK_GROUP(drink_group_id)
);

CREATE TABLE MATERIAL (
    material_id SERIAL PRIMARY KEY,
    material VARCHAR(255),
    quantity DECIMAL(10, 2),
    unit VARCHAR(50)
);

CREATE TABLE DRINK_MATERIAL (
    drink_id INT,
    material_id INT,
    m_quantity DECIMAL(10, 2),
    l_quantity DECIMAL(10, 2),
    PRIMARY KEY (drink_id, material_id),
    FOREIGN KEY (drink_id) REFERENCES DRINK(drink_id),
    FOREIGN KEY (material_id) REFERENCES MATERIAL(material_id)
);

CREATE TABLE CAKE (
    cake_id SERIAL PRIMARY KEY,
    cake VARCHAR(255),
    quantity INT,
    cost VARCHAR(50)
);

INSERT INTO DRINK_GROUP (drink_group) VALUES
('Trà'),
('Sinh Tố'),
('Nước Ép');

INSERT INTO DRINK (drink, m_cost, l_cost, drink_group_id) VALUES
('Trà Sữa Truyền Thống', 30, 35, 1),
('Trà Xanh Matcha', 35, 40, 1),
('Sinh Tố Xoài', 40, 45, 2),
('Nước Ép Cam', 35, 40, 3);

INSERT INTO MATERIAL (material, quantity, unit) VALUES
('Trà Đen', 1000, 'g'),
('Sữa Tươi', 500, 'ml'),
('Trà Xanh', 800, 'g'),
('Xoài', 50, 'piece'),
('Cam', 30, 'piece');

INSERT INTO DRINK_MATERIAL (drink_id, material_id, m_quantity, l_quantity) VALUES
(1, 1, 5, 7),
(1, 2, 150, 200),
(2, 3, 4, 6),
(3, 4, 3, 4),
(4, 5, 2, 4);

INSERT INTO CAKE (cake, quantity, cost) VALUES
('Bánh Mì', 100, '10'),
('Bánh Ngọt', 50, '20'),
('Bánh Flan', 70, '15');
