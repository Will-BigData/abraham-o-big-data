class BankError(Exception):  
  pass

class DuplicateAccountError(BankError):
  def __init__(self, name):
    self.message = f"An account with the name '{name}' already exists."
    super().__init__(self.message)

class AccountRetrievalError(BankError):
  def __init__(self, message = "An error occurred while retrieving account."):
    self.message = message
    super().__init__(self.message)

class InvalidEntryError(BankError):
  def __init__(self, value = None, message="Invalid entry. Please enter a valid positive number."):
    if value is not None:
      self.message = f"{message} You entered: {value}."
    else:
      self.message = message
    super().__init__(self.message)

class AccountNotFoundError(BankError):
  def __init__(self, value = None, message = f"Account not found."):
      if value is not None:
        self.message = f"Account with ID {value} not found."
      else:
        self.message = message
      super().__init__(self.message)

class InsufficientFundsError(BankError):
  def __init__(self, message = "Insufficient funds for withdrawal.") -> None:
    self.message = message
    super().__init__(self.message)

class TransactionError(BankError):
  def __init__(self, message = "An error occurred during this transaction."):
    self.message = message
    super().__init__(self.message)



