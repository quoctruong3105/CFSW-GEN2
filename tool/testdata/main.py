from data_feed import InventoryInsertor, AccountInsertor

if __name__ == "__main__":
    inventory_ist = InventoryInsertor()
    inventory_ist.insert_drink_groups()
    inventory_ist.insert_materials()
    inventory_ist.insert_drinks()
    inventory_ist.insert_drink_material()
    inventory_ist.insert_cakes()
    inventory_ist.insert_toppings()
    inventory_ist.db.conn.close()

    account_ist = AccountInsertor()
    account_ist.insert_accounts()
    account_ist.db.conn.close()
