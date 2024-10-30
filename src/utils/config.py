import os
from pathlib import Path
from typing import List

import tomli
from pydantic import BaseModel, Field, validator


class EmailRule(BaseModel):
    filter: str
    action: str


class EmailAccount(BaseModel):
    account_name: str
    account_token: str
    account_file: str
    rules: List[EmailRule] = []

    @validator("rules", pre=True)
    def parse_rules(cls, value):
        if isinstance(value, list):
            return [EmailRule(**rule) for rule in value]
        return []


class app_config(BaseModel):
    APP_NAME: str = "dystill"

    APP_HOME_DIR: Path = Field(
        default_factory=lambda app_name="dystill": Path(
            os.environ.get("APPDATA")
            or os.environ.get("XDG_CONFIG_HOME")
            or os.path.join(os.environ["HOME"], ".config"),
            app_name,
        )
    )

    accounts: List[EmailAccount] = []

    @validator("accounts", pre=True, always=True)
    def load_accounts(cls, value, values):
        accounts = []
        for toml_file in values["APP_HOME_DIR"].glob("account*.toml"):
            try:
                with open(toml_file, "rb") as file:
                    toml_data = tomli.load(file)
                    credentials_data = toml_data.get("credentials", {})
                    rules_data = toml_data.get("rules", [])
                    account_data = {
                        "account_file": str(toml_file),
                        "account_name": credentials_data.get("account_name"),
                        "account_token": credentials_data.get("account_token"),
                        "rules": rules_data,
                    }
                    accounts.append(EmailAccount(**account_data))
            except Exception as e:
                print(f"Error loading account details from {toml_file}: {e}")
        return accounts

    def print_helper_message(self):
        """Prints a helper message on how to configure accounts. Exits the program."""

        print("No accounts configured. To add an account:")
        print(f"\n1. Create a TOML file in {self.APP_HOME_DIR} named 'account*.toml'")
        print("\n2. Add account credentials and rules to it")
        print(
            "\n3. You can setup multiple accounts each in a separate TOML config file using `account` perfix:"
        )
        print("\taccount.toml\n\taccount2.toml\n\taccount-primary.toml")

    def __init__(self, *args, **kwargs):
        """Initializes the app_config, checks for accounts, and exits if none are found."""
        super().__init__(*args, **kwargs)
        # Exit the program if no accounts are found
        if not self.accounts:
            self.print_helper_message()
            exit(1)
