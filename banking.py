from random import randint, choices
from string import digits
import sqlite3


class Bank:
    def __init__(self):
        self.id = 0
        self.card_num = 0
        self.pin = 0
        self.balance = 0

    def lunh(self, card_num):
        acc = 0
        for i in range(1, len(card_num) + 1):
            step = int(card_num[i - 1])
            if i % 2 == 1:
                step *= 2
            if step > 9:
                step -= 9
            acc += step
        last_dig = str((10 * (acc // 10 + 1) - acc) % 10)
        if acc % 10 == 0:
            return card_num + last_dig, True
        else:
            return card_num + last_dig, False

    def gen_card(self, conn, cur):
        gen_card_num = str(randint(400000000000000, 400000999999999))
        card_num, flag = self.lunh(gen_card_num)
        pin = "".join(choices(digits, k=4))
        print("Your card has been created")
        print("Your card number:")
        print(card_num)
        print("Your card PIN:")
        print(pin)
        cur.execute(f"INSERT INTO card (number, pin, balance) VALUES ({card_num}, {pin}, {0})")
        conn.commit()

    def log_by_card(self, conn, cur):
        print("Enter your card number:")
        number_of_card = input()
        print("Enter your PIN:")
        pin_of_card = input()
        cur.execute(f"SELECT * FROM card WHERE number = {number_of_card}")
        res = cur.fetchone()
        if res and res[1] == number_of_card and res[2] == pin_of_card:
            print("\nYou have successfully logged in!\n")
            self.id = res[0]
            self.card_num = res[1]
            self.pin = res[2]
            self.balance = int(res[3])
            print(res)
            opt = self.logged_menu(conn, cur)
            return opt
        else:
            print("Wrong card number or PIN!")

    def check_balance(self, cur):
        cur.execute(f"SELECT balance FROM card WHERE number = {self.card_num}")
        res = cur.fetchone()[0]
        print(f"Balance: {res}")

    def add_income(self, cur):
        print("Enter income:")
        income = int(input())
        self.balance += income
        cur.execute(f"UPDATE card SET balance = balance + {income} WHERE number = {self.card_num}")

    def transfer(self, cur):
        print("Transfer")
        print("Enter card number:")
        card_num = input()
        cur.execute(f"SELECT number FROM card WHERE number = {card_num}")
        res = cur.fetchall()
        unn, check = self.lunh(card_num[:len(card_num)])
        if card_num == self.card_num:
            print("You can't transfer money to the same account!")
        elif not check:
            print("Probably you made a mistake in the card number. Please try again!")
        elif not res:
            print("Such a card does not exist.")
        else:
            print("Enter how much money you want to transfer:")
            amount_of_money = int(input())
            print(self.balance)
            if amount_of_money > self.balance:
                print("Not enough money!")
            else:
                self.balance -= amount_of_money
                cur.execute(f"UPDATE card SET balance = balance + {amount_of_money} WHERE number = {card_num}")
                cur.execute(f"UPDATE card SET balance = balance - {amount_of_money} WHERE number = {self.card_num}")
                print("Success!")

    def close_acc(self, cur):
        cur.execute(f"DELETE FROM card WHERE number = {self.card_num}")
        print("The account has been closed!")

    def logged_menu(self, conn, cur):
        while True:
            print("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")
            opt = input()
            print()
            if opt == "1":
                self.check_balance(cur)
            elif opt == "2":
                self.add_income(cur)
            elif opt == "3":
                self.transfer(cur)
            elif opt == "4":
                self.close_acc(cur)
            elif opt == "5":
                print("You have successfully logged out!")
                break
            elif opt == "0":
                return "0"
            print()
            conn.commit()

    def menu(self, conn, cur):
        opt = 1
        while opt != "0":
            print("""1. Create an account
2. Log into account
0. Exit""")
            opt = input()
            print()
            if opt == "1":
                self.gen_card(conn, cur)
            elif opt == "2":
                opt = self.log_by_card(conn, cur)
            elif opt == "0":
                print("Bye!")
                break
            print()


with sqlite3.connect('./card.s3db') as conn:
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)")
    conn.commit()
    bank = Bank()
    bank.menu(conn, cur)