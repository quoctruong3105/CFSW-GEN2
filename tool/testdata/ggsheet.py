import os
from const import DataMap as dm

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class DataInterface:
    def __init__(self):
        self.credentials = None
        self.sheets = None
        self.__setup_access_datasheet()

    def __setup_access_datasheet(self):
        if os.path.exists(dm.GGS_TOKEN_PATH):
            self.credentials = Credentials.from_authorized_user_file(
                dm.GGS_TOKEN_PATH, dm.SCOPES
            )
        if not self.credentials or not self.credentials.valid:
            if (
                self.credentials
                and self.credentials.expired
                and self.credentials.refresh_token
            ):
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    dm.GGS_CREDENTIALS_PATH, dm.SCOPES
                )
                self.credentials = flow.run_local_server(port=0)
            with open(dm.GGS_TOKEN_PATH, "w") as token:
                token.write(self.credentials.to_json())
        if self.credentials is None:
            exit(1)
        else:
            try:
                service = build("sheets", "v4", credentials=self.credentials)
                self.sheets = service.spreadsheets()
            except HttpError as error:
                print(error)
                exit()

    def __get_cell_value(self, sheet_name, cell):
        cell_value = (
            self.sheets.values()
            .get(spreadsheetId=dm.SPREADSHEET_ID, range=f"{sheet_name}!{cell}")
            .execute()
            .get("values")[0][0]
        )
        return cell_value

    def __get_range_value(self, sheet_name, range):
        range_value = (
            self.sheets.values()
            .get(spreadsheetId=dm.SPREADSHEET_ID, range=f"{sheet_name}!{range}")
            .execute()
            .get("values")
        )
        return range_value

    def fetch_raw_data(self, sheet, cell, range):
        last_row = data_inf.__get_cell_value(sheet, cell)
        raw_data = data_inf.__get_range_value(sheet, range % last_row)
        return raw_data


data_inf = DataInterface()
