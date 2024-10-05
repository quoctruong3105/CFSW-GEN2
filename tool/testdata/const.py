class DataMap:
    SCOPES               = ["https://www.googleapis.com/auth/spreadsheets"]
    SPREADSHEET_ID       = '13CCZ5lX2WMRZrqqvdvYJg8LYZp3c6UHkJtJwEhU578Q'
    GGS_CREDENTIALS_PATH = 'E:/CFSW-GEN2/tool/testdata/creds/ggsheet_creds.json'
    GGS_TOKEN_PATH       = 'E:/CFSW-GEN2/tool/testdata/creds/token.json'

    # constants for inventory sheet
    INVENTORY_SHEET      = 'inventory'
    # drink group
    DRINK_GRP_RANGE      = 'V3:V%s'
    DRINK_GRP_COUNT_CELL = 'W1'
    # drink
    DRINK_RANGE          = 'A3:F%s'
    DRINK_COUNT_CELL     = 'F1'
    # material
    MATERIAL_RANGE       = 'H3:J%s'
    MATERIAL_COUNT_CELL  = 'J1'
    # cake
    CAKE_RANGE           = 'L3:N%s'
    CAKE_COUNT_CELL      = 'N1'
    # topping
    TOPPING_RANGE        = 'P3:T%s'
    TOPPING_COUNT_CELL   = 'T1'

    # constants for account sheet
    ACCOUNT_SHEET        = 'account'
    # drink group
    ACCOUNT_RANGE        = 'A3:E%s'
    ACCOUNT_COUNT_CELL   = 'E1'
