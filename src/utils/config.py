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
                    account_data = tomli.load(file)
                    accounts.append(EmailAccount(**account_data))
            except Exception as e:
                print(f"Error loading account details from {toml_file}: {e}")
        return accounts

    def print_helper_message(self):
        """Prints a helper message on how to configure accounts. Exits the program."""

        print(f"No accounts configured. To add an account:")
        print(f"\n1. Create a TOML file in {self.APP_HOME_DIR} named 'account.toml'")
        print(f"\n2. Add the following data to the file (replace placeholders):")
        print(f"  ```toml")
        print(f"  [credentials]")
        print(f'  account_name = "YourAccountName"')
        print(f'  account_token = "YourAccountToken"')
        print(f"  rules = [")
        print(f"      # Add email rules here")
        print(
            f"      # Example:\n      { {'filter': 'from:example.com', 'action': 'spam'} }"
        )
        print(f"      { {'filter': 'subject:important', 'action': 'mark_important'} }")
        print(f"  ]")
        print(f"  ```")
        print(
            f"\n3. You can setup multiple accounts each in a separate TOML config file using `account` perfix:"
        )
        print(f"\taccount.toml\n\taccount2.toml\n\taccount-primary.toml")

    def __init__(self, *args, **kwargs):
        """Initializes the app_config, checks for accounts, and exits if none are found."""
        super().__init__(*args, **kwargs)
        # Exit the program if no accounts are found
        if not self.accounts:
            self.print_helper_message()
            exit(1)
