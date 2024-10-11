class BankError(Exception):  
  pass


class InsufficientFundsError(BankError):
  def __init__(self, message = "Insufficient funds for this transaction.") -> None:
    self.message = message
    super().__init__(self.message)

class InvalidNameError(BankError):
  def __init__(self, message = "This name is already taken or invalid."):
    self.message = message
    super().__init__(self.message)

class AccountNotFoundError(BankError):
  def __init__(self, message = "Account not found. Please check the name and try again."):
    self.message = message
    super().__init__(self.message)

class FileLoadError(BankError):
  def __init__(self, message = "Error loading data from file."):
    self.message = message
    super().__init__(self.message)

class FileSaveError(BankError):
  def __init__(self, message = "Error saving data to file."):
    self.message = message
    super().__init__(self.message)

class InvalidFileFormatError(BankError):
  def __init__(self, message = "Invalid file format detected."):
      self.message = message
      super().__init__(self.message)

class InvalidInputError(BankError):
  def __init__(self, message = "Invalid input provided. Please enter a valid value."):
    self.message = message
    super().__init__(self.message)

class InvalidEntryError(BankError):
    def __init__(self, value = None, message="Invalid entry. Please enter a valid positive number."):
      if value is not None:
        self.message = f"{message} You entered: {value}."
      else:
        self.message = message
      super().__init__(self.message)
