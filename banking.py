# # # # Write your code here
import random
import sqlite3


dbase = sqlite3.connect("card.s3db")

cur = dbase.cursor()

# if you start project without db please uncomment code from below
# and comment out after first launch

# cur.execute("DROP TABLE IF EXISTS card;")
# cur.execute("""CREATE TABLE IF NOT EXISTS card (
#             id INTEGER PRIMARY KEY,
#             number TEXT,
#             pin TEXT,
#             balance INTEGER DEFAULT 0
#             );""")

# cur.execute("""INSERT INTO card (number, pin) VALUES ("4000001830850202", "6311");""")
#
# cur.execute("""SELECT * FROM card""")
#
# print(cur.fetchall())
#
# dbase.commit()
# dbase.close()


def generate_card_num():
    a = random.randint(000000000, 999999999)
    card_num = (400000000000000 + a)
    card_num = str(card_num) + str(luna(card_num))
    return card_num


def luna(card_num):
    """Check if card is correct"""

    generate_flag = True
    if len(str(card_num)) == 16:
        generate_flag = False

    extra_card_num = []

    for i in enumerate(str(card_num)[0:len(str(card_num))]):
        num = int(i[1])
        if (i[0]+1) % 2 != 0:
            num *= 2
            if num > 9:
                num -= 9
            extra_card_num.append(num)
        else:
            extra_card_num.append(num)
    extra_card_sum = sum(extra_card_num)
    if generate_flag:
        last_num = 10 - (extra_card_sum % 10)
        if last_num == 10:
            last_num = 0
        return last_num
    else:
        if extra_card_sum % 10 == 0:
            return True
        return False


class Card:
    """Card in bank system"""
    def __init__(self, num=None, pin=None):
        self.card_num = num
        self.card_pin = pin
        self.__card_balance = 0
        if self.card_num and self.card_pin is not None:
            cur.execute(f"""SELECT balance FROM card WHERE number = {self.card_num} AND pin = {self.card_pin};""")
            self.__card_balance = cur.fetchone()[0]

    def create_card(self):

        # generate card
        self.card_num = generate_card_num()

        b = random.randint(0, 9999)
        self.card_pin = str(b).zfill(4)

        # save created card in DataBase
        cur.execute(f"""INSERT INTO card (number, pin) VALUES ({str(self.card_num)}, {self.card_pin})""")

        dbase.commit()

        print("\nYour card has been created")
        print("Your card number:\n{}".format(self.card_num))
        print("Your card PIN:\n{}\n".format(self.card_pin))

    @property
    def get_balance(self):
        return self.__card_balance

    def set_balance(self, deposit):
        self.__card_balance += deposit
        cur.execute(f"""UPDATE card SET balance = balance + {deposit} WHERE number = {str(self.card_num)};""")
        dbase.commit()


def card_checkout(card_num, card_pin):
    db_statement = """SELECT * FROM card"""
    cur.execute(db_statement)
    card_list = cur.fetchall()
    flag = False
    for card in card_list:
        if str(card_num) == card[1] and card_pin == card[2]:
            flag = True
            break
    return flag


def start_menu():
    print("1. Create an account\n2. Log into account\n0. Exit")
    user_choice = int(input(">"))
    return user_choice


def add_income(user_card):
    print("\nEnter income:")
    deposit = int(input(">"))
    user_card.set_balance(deposit)
    print("Income was added!\n")


def transfer_money(user_card):
    print("\nTransfer")
    print("Enter card number:")
    transfer_card = int(input(">"))
    if luna(transfer_card):
        if transfer_card == user_card.card_num:
            print("You can't transfer money to the same account!\n")
            return
        cur.execute(f"""SELECT number FROM card WHERE number = {str(transfer_card)};""")
        if cur.fetchone():
            print("Enter how much money you want to transfer:")
            deposit = int(input(">"))
            if not deposit > user_card.get_balance:
                user_card.set_balance(-deposit)
                cur.execute(f"""UPDATE card SET balance = balance + {deposit} WHERE number = {transfer_card};""")
                dbase.commit()
                print("Success!\n")
            else:
                print("Not enough money!\n")
        else:
            print("Such a card does not exist.\n")
    else:
        print("Probably you made a mistake in the card number. Please try again!\n")


def close_account(user_card):
    cur.execute(f"""DELETE FROM card WHERE number = {str(user_card.card_num)};""")
    dbase.commit()
    print("The account has been closed!\n")


def card_menu(user_card):

    while True:
        print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
        user_input = int(input(">"))

        if user_input == 1:
            print(f"\nBalance: {user_card.get_balance}\n")
        elif user_input == 2:
            add_income(user_card)
        elif user_input == 3:
            transfer_money(user_card)
        elif user_input == 4:
            close_account(user_card)
            return
        elif user_input == 5:
            return
        elif user_input == 0:
            exit()
        else:
            print("Non correct input!")


def log_into_account():
    print("\nEnter your card number:")
    card_num = int(input())

    print("Enter your PIN:")
    card_pin = input(">")

    if card_checkout(card_num, card_pin):
        user_card = Card(card_num, card_pin)
        print("\nYou have successfully logged in!")
        card_menu(user_card)
    else:
        print("\nWrong card number or PIN!\n")


def main():

    while True:
        user_choice = start_menu()

        if user_choice == 1:
            user_card = Card()
            user_card.create_card()
        elif user_choice == 2:
            log_into_account()
        elif user_choice == 0:
            print("\nBye!")
            exit()
        else:
            print("Non correct input!")


if __name__ == '__main__':
    main()
    dbase.close()
