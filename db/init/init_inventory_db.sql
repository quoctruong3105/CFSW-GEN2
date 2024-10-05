------------------------------------------------
-- Init database for inventory service
------------------------------------------------
CREATE DATABASE "inventory";

\c "inventory"

CREATE TABLE DRINK_GROUP (
    drink_group_id SERIAL PRIMARY KEY,
    drink_group VARCHAR(255) UNIQUE
);

CREATE TABLE DRINK (
    drink_id SERIAL PRIMARY KEY,
    drink VARCHAR(255) UNIQUE,
    m_cost DECIMAL(10, 2),
    l_cost DECIMAL(10, 2),
    drink_group_id INT,
    FOREIGN KEY (drink_group_id) REFERENCES DRINK_GROUP(drink_group_id)
);

CREATE TABLE MATERIAL (
    material_id SERIAL PRIMARY KEY,
    material VARCHAR(255) UNIQUE,
    quantity DECIMAL(10, 2),
    unit VARCHAR(10)
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
    cake VARCHAR(255) UNIQUE,
    cost DECIMAL(10, 2),
    quantity INT
);

CREATE TABLE TOPPING (
    topping_id SERIAL PRIMARY KEY,
    topping VARCHAR(255) UNIQUE,
    cost DECIMAL(10, 2),
    quantity INT,
    unit VARCHAR(10),
    quantity_per_drink INT
);
