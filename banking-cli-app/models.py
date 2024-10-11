import csv
import json
from datetime import datetime
from exceptions import InsufficientFundsError, InvalidEntryError, InvalidNameError, AccountNotFoundError, InvalidFileFormatError, FileLoadError, FileSaveError, InvalidInputError


class Account:
  def __init__(self, account_id, name, balance = 0.0):
    self.account_id = account_id
    self.name = name
    self.balance = balance
    self.transactions = []

  def deposit(self, amount):
    try:
      amount = float(amount)
      if amount <= 0:
        raise InvalidEntryError()
      self.balance += amount
      self.transactions.append({
        'type': 'deposit',
        'amount': amount,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    except (ValueError, TypeError):
      raise InvalidEntryError()

  def withdraw(self, amount):
    try:
      amount = float(amount)
      if amount <= 0:
        raise InvalidEntryError()
      if amount > self.balance:
        raise InsufficientFundsError()
      self.balance -= amount
      self.transactions.append({
        'type': 'withdrawal',
        'amount': amount,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      })
    except (ValueError, TypeError):
      raise InvalidEntryError()

  def get_transactions(self):
    return self.transactions

  def get_balance(self):
    return self.balance
  

class Bank:

  MORTGAGE_REQUIREMENT = 10000.0
  
  def __init__(self):
    self.accounts = []
    self.unique_names = set()

  def create_account(self, name, balance = 0.0):

    if name in self.unique_names:
      raise InvalidNameError(f"Name '{name}' is not available. Please choose a different name.")
    
    self.unique_names.add(name)
    print(f"New user '{name}' registered.")

    account_id = len(self.accounts) + 1
    account = Account(account_id, name, balance)
    self.accounts.append(account)
    return account
  
  def get_total_balance_for_user(self, name):
    total_balance = sum(account.get_balance() for account in self.accounts if account.name == name)
    return total_balance

  def get_account(self, account_id):
    for account in self.accounts:
      if account.account_id == account_id:
        return account
    return None

  def apply_for_mortgage(self, name):
    total_balance = self.get_total_balance_for_user(name)
    if total_balance >= self.MORTGAGE_REQUIREMENT:
      return f"{name} qualifies for a mortgage."
    else: 
      return f"Hello {name}, you would need a balance of {self.MORTGAGE_REQUIREMENT} to qualify."
  
  def load_account_data_from_csv_file(self, filename):
    try:
      with open(filename, mode = 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
          try:
            account_id = int(row['account_id'])
            name = row['name']
            balance = float(row['balance'])

            account = Account(account_id, name, balance)
            self.accounts.append(account)
          except (ValueError, KeyError) as e:
            raise InvalidFileFormatError(f"Invalid data format in file: {e}")

      print(f"Data loaded successfully from {filename}")
    except FileNotFoundError:
      raise FileLoadError(f"File {filename} not found. Generating new file...")
    except PermissionError:
        raise FileLoadError(f"Permission denied when accessing file '{filename}'.")

  def save_account_data_to_csv_file(self, filename):
    try:
      with open(filename, 'w', newline='') as file:
        fieldnames = ['account_id', 'name', 'balance']
        writer = csv.DictWriter(file, fieldnames = fieldnames)
        writer.writeheader()

        for account in self.accounts:
          writer.writerow({
            'account_id': account.account_id,
            'name': account.name,
            'balance': account.get_balance()
          })
    except PermissionError:
            raise FileSaveError(f"Permission denied when saving file '{filename}'.")
    except Exception as e:
        raise FileSaveError(f"An error occurred while saving the file: {e}")

  def print_receipt(self, name, filename):

    try:
      transactions = []
      for account in self.accounts:
        if account.name == name:
          transactions.append({
            'account_id': account.account_id,
            'balance': account.get_balance(),
            'transactions': account.get_transactions()
          })

      if not transactions:
        raise AccountNotFoundError(f"No accounts found for name: {name}")
      
      receipt_data = {
          "name": name,
          "transactions": transactions,
          "total_balance": sum(account.get_balance() for account in self.accounts if account.name == name)
      }

      with open(filename, 'w') as json_file:
        json.dump(receipt_data, json_file, indent=4)
        print(f"Receipt saved at {filename}")
      return    
    except AccountNotFoundError as e:
      print(e.message)
    except InvalidInputError as e:
      print(e.message)
