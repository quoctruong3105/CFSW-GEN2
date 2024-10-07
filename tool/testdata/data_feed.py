from datetime import datetime

# from ggsheet import data_inf
from database import Database
from const import DataMap as dm
from dummy_data import InventoryData as ivn_data, AccountData as acc_data


class InventoryInsertor:
    def __init__(self):
        self.db = Database(dbname="inventory")

    def insert_drink_groups(self):
        query = "INSERT INTO DRINK_GROUP (drink_group) VALUES (%s);"
        # data = data_inf.fetch_raw_data(dm.INVENTORY_SHEET, dm.DRINK_GRP_COUNT_CELL, dm.DRINK_GRP_RANGE)
        data = ivn_data.drink_group
        data = [(group_name[0],) for group_name in data]
        self.db.insert(query, data)

    def insert_materials(self):
        query = "INSERT INTO MATERIAL (material, quantity, unit) VALUES (%s, %s, %s);"
        # data = data_inf.fetch_raw_data(dm.INVENTORY_SHEET, dm.MATERIAL_COUNT_CELL, dm.MATERIAL_RANGE)
        data = ivn_data.material
        data = [(d[0], d[1], d[2]) for d in data]
        self.db.insert(query, data)

    def insert_drinks(self):
        query = "INSERT INTO DRINK (drink, m_cost, l_cost, drink_group_id) VALUES (%s, %s, %s, %s);"
        # data = data_inf.fetch_raw_data(dm.INVENTORY_SHEET, dm.DRINK_COUNT_CELL, dm.DRINK_RANGE)
        data = ivn_data.drink
        data = [(m[0], float(m[1]), float(m[2]), int(m[5])) for m in data]
        self.db.insert(query, data)

    def insert_cakes(self):
        query = "INSERT INTO CAKE (cake, cost, quantity) VALUES (%s, %s, %s);"
        # data = data_inf.fetch_raw_data(dm.INVENTORY_SHEET, dm.CAKE_COUNT_CELL, dm.CAKE_RANGE)
        data = ivn_data.cake
        data = [(m[0], float(m[1]), int(m[2])) for m in data]
        self.db.insert(query, data)

    def insert_toppings(self):
        query = "INSERT INTO TOPPING (topping, cost, quantity, unit, quantity_per_drink) VALUES (%s, %s, %s, %s, %s);"
        # data = data_inf.fetch_raw_data(dm.INVENTORY_SHEET, dm.TOPPING_COUNT_CELL, dm.TOPPING_RANGE)
        data = ivn_data.topping
        data = [(m[0], float(m[1]), int(m[2]), m[3], int(m[4])) for m in data]
        self.db.insert(query, data)

    def insert_drink_material(self):
        query = "INSERT INTO DRINK_MATERIAL (drink_id, material_id, m_quantity, l_quantity) VALUES (%s, %s, %s, %s);"
        # data = data_inf.fetch_raw_data(dm.INVENTORY_SHEET, dm.DRINK_COUNT_CELL, dm.DRINK_RANGE)
        # drink_material_data = []

        # for i, d in enumerate(data, start=1):
        #     m_comp = d[3].split("-")
        #     l_comp = d[4].split("-")
        #     for i_comp, m_item in enumerate(m_comp):
        #         material_id = m_item.split(":")[0]
        #         m_quantity = m_item.split(":")[1]
        #         l_quantity = l_comp[i_comp].split(":")[1]

        #         drink_material_data.append(
        #             (i, int(material_id), float(m_quantity), float(l_quantity))
        #         )
        drink_material_data = ivn_data.drink_material
        self.db.insert(query, drink_material_data)


class AccountInsertor:
    def __init__(self):
        self.db = Database(dbname="account")

    def insert_accounts(self):
        query = "INSERT INTO ACCOUNT (username, password, role, last_login, last_logout) VALUES (%s, %s, %s, %s, %s);"
        # data = data_inf.fetch_raw_data(dm.ACCOUNT_SHEET, dm.ACCOUNT_COUNT_CELL, dm.ACCOUNT_RANGE)
        data = acc_data.account
        data = [
            (
                m[0],
                m[1],
                m[2],
                datetime.strptime(m[3], "%Y-%m-%d %H:%M:%S").strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if len(m) > 3
                else None,
                datetime.strptime(m[4], "%Y-%m-%d %H:%M:%S").strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if len(m) > 4
                else None,
            )
            for m in data
        ]
        self.db.insert(query, data)
