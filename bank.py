import psycopg2

class Bank:

    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname="bank_database",
                user="postgres",
                password="root",
                host="localhost",
                port="5432"
            )
            self.cursor = self.conn.cursor()
            self.logged_in_account = None
        except Exception as e:
            print("Bank Server is down:", e)

    def mainMenu(self):
        while True:
            print("\nWelcome to the Bank of Awais")
            print("1. Register Account")
            print("2. Login")
            print("3. Exit")

            try:
                choice = int(input("Enter your choice: "))
            except ValueError:
                print("Please enter a valid number.")
                continue

            if choice == 1:
                self.registerAccount()
            elif choice == 2:
                self.loginAccount()
                if self.logged_in_account:
                    self.userMenu()
            elif choice == 3:
                self.cursor.close()
                self.conn.close()
                print("Exiting...")
                exit()
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    def userMenu(self):
        while True:
            print("\n--- Account Services Menu ---")
            print("1. Check Balance")
            print("2. Deposit Money")
            print("3. Withdraw Money")
            print("4. Transfer Money")
            print("5. View Account Details")
            print("6. Compare with Other Accounts")
            print("7. Logout")

            try:
                choice = int(input("Enter your choice: "))
            except ValueError:
                print("Please enter a valid number.")
                continue

            if choice == 1:
                self.checkBalance()
            elif choice == 2:
                self.depositBalance()
            elif choice == 3:
                self.withdrawBalance()
            elif choice == 4:
                self.TransferBalance()
            elif choice == 5:
                self.viewDetails()
            elif choice == 6:
                self.compareAccounts()
            elif choice == 7:
                print("Logging out...")
                self.logged_in_account = None
                break
            else:
                print("Invalid choice. Try again.")

    def registerAccount(self):
        try:
            print("\n--- Register New Account ---")
            name = input("Enter your full name: ")
            age = int(input("Enter your age: "))
            email = input("Enter your email: ")
            phone = input("Enter your phone number: ")
            password = input("Set your password: ")
            account_type = input("Enter account type (Savings / Current): ")
            if account_type.lower() not in ["savings", "current"]:
                while account_type.lower() not in ["savings", "current"]:
                    print("Account type can only be Savings or Current")
                    account_type = input("Enter account type (Savings / Current): ")
            balance = float(input("Enter your opening balance: "))

            self.cursor.execute("SELECT MAX(account_number) FROM accounts")
            result = self.cursor.fetchone()
            if result[0] is None:
                prev_acc_number = 0
            else:
                prev_acc_number = result[0]

            new_account_number = prev_acc_number + 1

            self.cursor.execute("""
                INSERT INTO accounts (name, age, email, phone, password, account_type, balance, account_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, age, email, phone, password, account_type, balance, new_account_number))

            self.conn.commit()
            print(f" Account registered successfully!")
            print(f"Your account number is: {new_account_number}")

        except Exception as e:
            print("Error registering account:", e)

    def loginAccount(self):
        try:
            print("\n--- Login to Your Account ---")
            email = input("Enter your registered email: ")
            password = input("Enter your password: ")

            self.cursor.execute("""
                SELECT name, age, email, phone, account_type, balance, account_number 
                FROM accounts 
                WHERE email = %s AND password = %s
            """, (email, password))
            account = self.cursor.fetchone()

            if account:
                self.logged_in_account = account[6]
            else:
                print("Login failed: Incorrect email or password.")
                self.logged_in_account = None

        except Exception as e:
            print("Error during login:", e)

    def viewDetails(self):
        try:
            if self.logged_in_account is None:
                print("You must be logged in to view details.")
                return

            self.cursor.execute("""
                SELECT name, account_number, account_type, balance
                FROM accounts
                WHERE account_number = %s
            """, (self.logged_in_account,))
            result = self.cursor.fetchone()

            if result:
                print("\n--- Account Details ---")
                print(f"Name           : {result[0]}")
                print(f"Account Number : {result[1]}")
                print(f"Account Type   : {result[2]}")
                print(f"Balance        : Rs. {result[3]:,.2f}")
            else:
                print("Account not found.")
        except Exception as e:
            print("Error fetching account details:", e)

    def checkBalance(self):
        try:
            if self.logged_in_account is None:
                print("You must be logged in to check your balance.")
                return

            self.cursor.execute("""
                SELECT name, balance FROM accounts 
                WHERE account_number = %s
            """, (self.logged_in_account,))

            result = self.cursor.fetchone()

            if result:
                print("\nAccount Balance")
                print(f"Name    : {result[0]}")
                print(f"Balance : Rs. {result[1]:,.2f}")
            else:
                print("Account not found.")

        except Exception as e:
            print("Error checking balance:", e)

    def depositBalance(self):
        try:
            if self.logged_in_account is None:
                print("You must be logged in to deposit money.")
                return

            amount = float(input("Enter amount to deposit: "))
            if amount <= 0:
                print("Amount must be greater than 0.")
                return

            self.cursor.execute("""
                SELECT balance FROM accounts WHERE account_number = %s
            """, (self.logged_in_account,))
            result = self.cursor.fetchone()

            if result:
                current_balance = result[0]
                new_balance = current_balance + amount

                self.cursor.execute("""
                    UPDATE accounts SET balance = %s WHERE account_number = %s
                """, (new_balance, self.logged_in_account))
                self.conn.commit()

                print(f"\nDeposit successful!")
                print(f"New Balance: Rs. {new_balance:}")
            else:
                print("Account not found.")

        except ValueError:
            print("Invalid input. Please enter a numeric value.")
        except Exception as e:
            print("Error during deposit:", e)

    def withdrawBalance(self):
        try:
            if self.logged_in_account is None:
                print("You must be logged in to withdraw money.")
                return

            amount = float(input("Enter the amount to be withdrawn: "))
            if amount <= 0:
                print("Amount must be greater than 0.")
                return

            self.cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (self.logged_in_account,))
            result = self.cursor.fetchone()

            if result:
                current_balance = result[0]

                if amount > current_balance:
                    print("Insufficient balance. Withdrawal denied.")
                    return

                new_balance = current_balance - amount
                self.cursor.execute("UPDATE accounts SET balance = %s WHERE account_number = %s",
                                    (new_balance, self.logged_in_account))
                self.conn.commit()

                print(f"\n Withdrawal successful.")
                print(f"New Balance: Rs. {new_balance:,.2f}")
            else:
                print("Account not found.")

        except ValueError:
            print("Invalid input. Please enter a numeric amount.")
        except Exception as e:
            print("Error during withdrawal:", e)

    def TransferBalance(self):
        try:
            if self.logged_in_account is None:
                print("You must be logged in to transfer money.")
                return

            to_acc = int(input("Enter recipient's account number: "))
            amount = float(input("Enter amount to transfer: "))

            if amount <= 0:
                print("Amount must be greater than 0.")
                return

            self.cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (self.logged_in_account,))
            sender_result = self.cursor.fetchone()

            self.cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (to_acc,))
            receiver_result = self.cursor.fetchone()

            if not sender_result:
                print("Your account not found.")
            elif not receiver_result:
                print("Recipient account not found.")
            elif amount > sender_result[0]:
                print("Insufficient balance. Transfer denied.")
            else:
                new_sender_balance = sender_result[0] - amount
                new_receiver_balance = receiver_result[0] + amount

                self.cursor.execute("UPDATE accounts SET balance = %s WHERE account_number = %s",
                                    (new_sender_balance, self.logged_in_account))
                self.cursor.execute("UPDATE accounts SET balance = %s WHERE account_number = %s",
                                    (new_receiver_balance, to_acc))
                self.conn.commit()

                print("Transfer successful.")
                print(f"Your New Balance: Rs. {new_sender_balance:,.2f}")

        except ValueError:
            print("Invalid input. Please enter numbers only.")
        except Exception as e:
            print("Error during transfer:", e)

    def compareAccounts(self):
        try:
            if self.logged_in_account is None:
                print("You must be logged in to Compare Accounts.")
                return
            other_acc_number = input("Enter the account number to compare with: ")

            self.cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (self.logged_in_account,))
            my_result = self.cursor.fetchone()

            self.cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (other_acc_number,))
            other_result = self.cursor.fetchone()

            if not other_result:
                print("The account number you're comparing with does not exist.")
                return

            my_balance = my_result[0]
            other_balance = other_result[0]

            print(f"\nYour Balance  : {my_balance}")
            print(f"Other Account Balance (Acc {other_acc_number}): {other_balance}")

            if my_balance > other_balance:
                print("Your account is bigger. ")
            elif my_balance < other_balance:
                print("Your account is smaller.")
            else:
                print("⚖ Both accounts have equal balance.")

        except Exception as e:
            print("Error while comparing accounts:", e)


if __name__ == '__main__':
    bank = Bank()
    bank.mainMenu()
