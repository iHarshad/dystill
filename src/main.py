from .utils.config import app_config

config = app_config()

for account in config.accounts:
    print(f"\nAccount Name: {account.account_name}")
    print(f"Account Token: {account.account_token}")
    for rule in account.rules:
        print(f"    Filter: {rule.filter}")
        print(f"    Action: {rule.action}")
