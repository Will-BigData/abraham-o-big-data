from decimal import Decimal, ROUND_DOWN
import sys
from models import Bank, Account
from mysql.connector import Error
from exceptions import DuplicateAccountError, AccountRetrievalError, InvalidEntryError, AccountNotFoundError, InsufficientFundsError, TransactionError


class Handler:
    def __init__(self):
        self.bank = Bank()

    def run(self):

        available_options = {
            '1': self.handle_open_new_account,
            '2': self.handle_make_deposit,
            '3': self.handle_make_withdrawal,
            '4': self.handle_get_balance,
            '5': self.handle_apply_for_mortgage,
            '6': self.exit_program
        }
        
        while True:
            self.cli_options()
            choice = input("Choose an option [1 - 6]: ")
            if choice in available_options:
                available_options[choice]()
            else:
                print("Invalid option. Please choose again.")
    
    def cli_options(self):
        print("\nWelcome to CLI Banking App")
        print("1. Open A New Account")
        print("2. Make A Deposit")
        print("3. Make A Withdrawal")
        print("4. Get Balance")
        print("5. Apply For Mortgage")
        print("6. Exit")

    def handle_open_new_account(self):
        name = input("Enter your name: ")
        try:
            account_id = self.bank.create_account(name)
            if account_id:
                print(f"Account created successfully for {name}. Account ID: {account_id}")
        except (DuplicateAccountError, Error) as e:
            print(e.message)

    def handle_make_deposit(self):
        try:
            account_id = input("Enter account ID: ")
            account = Account.get_account(account_id) 
            if account:
                amount = input("Enter deposit amount: ")
   
                balance = self.bank.deposit(account_id, amount)

                print(f"Deposited {float(amount)}. New balance: {balance.quantize(Decimal('0.00'), rounding=ROUND_DOWN)}")

        except (InvalidEntryError, AccountNotFoundError, TransactionError) as e:
            print(e.message)  

    def handle_make_withdrawal(self):
        try:
            account_id = input("Enter account ID: ")
            account = Account.get_account(account_id)
            if account:
                amount = input("Enter withdrawal amount: ")
                balance = self.bank.withdraw(account_id, amount)

                print(f"Withdrew {amount}. New balance: ${balance.quantize(Decimal('0.00'), rounding=ROUND_DOWN)}")
        except (InvalidEntryError, AccountNotFoundError, InsufficientFundsError, TransactionError) as e:
            print(e.message)

    def handle_get_balance(self):
        try:
            account_id = input("Enter account ID: ")
            account = Account.get_account(account_id)
            if account:
                print(f"Account balance: {account[2].quantize(Decimal('0.00'), rounding=ROUND_DOWN)}")
        except (InvalidEntryError, AccountNotFoundError, TransactionError) as e:
            print(e.message)

    def handle_apply_for_mortgage(self):
            account_id = input("Enter account ID: ")
            result = self.bank.apply_for_mortgage(account_id)
            print(result)

    def exit_program(self):
        print("Would you like a receipt? (yes/no)")
        want_receipt = input().strip().lower()
        if want_receipt == 'yes' or want_receipt == 'y':
            self.print_receipt()
        print("Exiting the program...")
        print("Goodbye!")
        sys.exit()

    def print_receipt(self):
        name = input("Enter your name: ")
        account_id = input("Enter your account ID: ")
        receipt_filepath = 'datasource/receipt.json'
        try:
            self.bank.print_receipt(name, account_id, receipt_filepath)
        except (AccountNotFoundError, AccountRetrievalError) as e:
            print(e.message)

if __name__ == "__main__":
    Handler().run()