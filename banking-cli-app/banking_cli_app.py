import sys
import os
from models import Bank
from exceptions import InvalidNameError, InvalidEntryError, InsufficientFundsError, FileLoadError, FileSaveError


class Handler:
    def __init__(self):
        self.bank = Bank()

    def run(self):

        self.load_data()

        available_options = {
            '1': self.handle_open_new_account,
            '2': self.handle_make_deposit,
            '3': self.handle_make_withdrawal,
            '4': self.handle_get_balance,
            '5': self.handle_apply_for_mortgage,
            '6': self.exit_program
        }
        
        while True:
            self.display_menu()
            choice = input("Choose an option [1 - 6]: ")
            if choice in available_options:
                available_options[choice]()
            else:
                print("Invalid option. Please choose again.")
    
    def display_menu(self):
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
            account = self.bank.create_account(name)
            if account is not None:
                try:
                    initial_balance = input("Enter initial deposit amount: ")
                    account.deposit(initial_balance)
                    print(f"Account created with ID: {account.account_id}, Name: {account.name}")
                except InvalidEntryError as e:
                    print(e.message)
            
            else: print("Returning to main menu.")
        except InvalidNameError as e:
            print(e.message)
        except InvalidEntryError as e:
            print("Invalid input. Please try again.")

    def handle_make_deposit(self):
        try:
            account = self.find_account_by_id()
            if account:
                amount = input("Enter deposit amount: ")
                account.deposit(amount)
                print(f"Deposited {amount}. New balance: {account.get_balance()}")
        except InvalidEntryError as e:
            print(e.message)       

    def handle_make_withdrawal(self):
        try:
            account = self.find_account_by_id()
            if account:
                amount = input("Enter withdrawal amount: ")
                account.withdraw(amount)
                print(f"Withdrew {amount}. New balance: ${account.get_balance():.2f}")
        except InvalidEntryError as e:
            print(e.message)
        except InsufficientFundsError as e:
            print(e.message)

    def handle_get_balance(self):
        try:
            account = self.find_account_by_id()
            if account:
                print(f"Account balance: {account.get_balance()}")
        except InvalidEntryError as e:
            print(e.message)

    def handle_apply_for_mortgage(self):
        name = input("Enter your name: ")
        result = self.bank.apply_for_mortgage(name)
        print(result)

    def exit_program(self):
        print("Would you like a receipt? (yes/no)")
        want_receipt = input().strip().lower()
        if want_receipt == 'yes' or want_receipt == 'y':
            self.print_receipt()
        print("Exiting the program...")
        print("Goodbye!")
        self.save_data()
        sys.exit()

    def print_receipt(self):
        name = input("Please enter your name for the receipt: ")
        receipt_filename = 'datasource/receipt.json'

        os.makedirs(os.path.dirname(receipt_filename), exist_ok=True)
        self.bank.print_receipt(name, receipt_filename)

    def find_account_by_id(self): 
        try:
            account_id_input = input("Enter account ID: ")
            account_id = int(account_id_input)
            account = self.bank.get_account(account_id)
            if not account:
                print("Account not found")
            return account
        except ValueError:   
            raise InvalidEntryError(value = account_id_input, message = "Account ID must be a valid integer")

    def load_data(self):
        try:
            self.bank.load_account_data_from_csv_file('datasource/accounts.csv')
        except FileLoadError as e:
            print(e.message)

    def save_data(self):
        try:
            self.bank.save_account_data_to_csv_file('datasource/accounts.csv')
        except FileSaveError as e:
            print(e.message)

if __name__ == "__main__":
    Handler().run()