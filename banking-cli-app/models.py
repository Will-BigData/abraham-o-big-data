import os
import json
from decimal import Decimal, ROUND_DOWN
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from db_config import db_config
from exceptions import DuplicateAccountError, AccountRetrievalError, TransactionError, InsufficientFundsError, InvalidEntryError, AccountNotFoundError



class Account:
  def __init__(self, account_id, name, bank):
    self.account_id = account_id
    self.name = name
    self.bank = bank

  @classmethod
  def get_account(cls, account_id):
    try:
      account_id = int(account_id)
    except ValueError:   
      raise InvalidEntryError(value = account_id)

    try:
      conn = mysql.connector.connect(**db_config)
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM accounts WHERE account_id = %s", (account_id,))
      account = cursor.fetchone()
      if not account:
        raise AccountNotFoundError(value=account_id)
      return account
    except Error as e:
      raise AccountRetrievalError()
    finally:
      cursor.close()
      conn.close()

class Bank:

  MORTGAGE_REQUIREMENT = 10000.0
  
  def __init__(self):
    self.conn = mysql.connector.connect(**db_config)
    self.cursor = self.conn.cursor()
    self.session_transactions = []

  def create_account(self, name):
    try:
      self.cursor.execute("SELECT * FROM accounts WHERE name = %s", (name,))
      existing_account = self.cursor.fetchone()

      if existing_account:
        raise DuplicateAccountError(name)
    
      self.cursor.execute("INSERT INTO accounts (name, balance) VALUES (%s, %s)", (name, 0))
      self.conn.commit()

      self.cursor.execute("SELECT account_id FROM accounts WHERE name = %s", (name,))
      account_id = self.cursor.fetchone()[0]
      return account_id
    except Error as e:
      print(f"An error occurred while creating the account: {e}")
      self.conn.rollback()
        
  def deposit(self, account_id, amount):
      try:
        amount = float(amount)
        if amount <= 0:
          raise InvalidEntryError(value=amount)
      except (ValueError, TypeError):
        raise InvalidEntryError(value=amount)

      self.cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
      balance = self.cursor.fetchone()[0]

      new_balance = balance + Decimal(amount)
      try:
        self.cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_balance, account_id))
        self.conn.commit()

        self.cursor.execute("INSERT INTO transactions (account_id, amount, transaction_type) " + 
                            "VALUES (%s, %s, 'deposit')", (account_id, amount))
        self.conn.commit()

        self.session_transactions.append({
        'account_id': account_id,
        'transaction_type': 'deposit',
        'amount': float(amount),
        'balance': float(new_balance),
        "transaction_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })    

      except Error as e:
        print(f"Error updating balance: {e}")
        self.conn.rollback()

      return new_balance

  def withdraw(self, account_id, amount):
    try:
      amount = float(amount)
      if amount <= 0:
        raise InvalidEntryError(value=amount)
    except (ValueError, TypeError):
      raise InvalidEntryError(value=amount)
    
    self.cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
    current_balance = self.cursor.fetchone()[0]

    if current_balance < amount:
      raise InsufficientFundsError()
    balance = current_balance - Decimal(amount)
    try:
      self.cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (balance, account_id))
      self.conn.commit()


      self.cursor.execute("INSERT INTO transactions (account_id, amount, transaction_type) VALUES (%s, %s, 'withdrawal')",
          (account_id, amount))
      self.conn.commit()

      self.session_transactions.append({
        'account_id': account_id,
        'transaction_type': 'withdrawal',
        'amount': float(amount),
        'balance': float(balance),
        'transaction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      })
    except Error as e:
      print(f"Error updating balance: {e}")
      self.conn.rollback()

    return balance

  def get_balance(self, account_id):
    try:
      account = Account.get_account(account_id)
    except (InvalidEntryError, AccountNotFoundError, TransactionError) as e:
      raise AccountRetrievalError(e.message)

    return account[2].quantize(Decimal('0.00'), rounding=ROUND_DOWN)

  def apply_for_mortgage(self, account_id):
    try:
      balance = self.get_balance(account_id)
    except AccountRetrievalError as e:
      print(e.message)
      return ""

    if balance >= self.MORTGAGE_REQUIREMENT:
      return f"Account {account_id} qualifies for a mortgage."
    else: 
      return f"Account {account_id} would need a balance of {self.MORTGAGE_REQUIREMENT} to qualify."

  def print_receipt(self, name, account_id, receipt_filepath):

    try:
      self.cursor.execute("SELECT * FROM accounts WHERE name = %s AND account_id = %s", 
                          (name, account_id))
      account = self.cursor.fetchone()     
      if not account:
          raise AccountNotFoundError(message = f"No account found for {name} with ID {account_id}. Cannot print receipt.")

    except Error as e:
      raise AccountRetrievalError()

    try:
      receipt_data = {
        "transactions": self.session_transactions
      }

      os.makedirs(os.path.dirname(receipt_filepath), exist_ok=True)

      with open(receipt_filepath, 'w') as receipt_file:
        json.dump(receipt_data, receipt_file, indent=4)
      print(f"Receipt saved to {receipt_filepath}")
      
    except Error as e:
      print(f"Error occurred while printing the receipt: {e}")
    except Exception as e:
      print(f"An unexpected error occurred: {e}")