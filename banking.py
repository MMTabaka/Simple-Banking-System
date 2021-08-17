import sqlite3
import random
from sys import exit

# setting a database
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

# creating a table with accounts
cur.execute('CREATE TABLE IF NOT EXISTS card '
            '(id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')
conn.commit()


# Generates a card number starting with 400000 and able to pass the Luhn algorithm
def generate_card_number():
    card_number = '400000'
    sum_of_digits = 8

    for i in range(9):
        digit = random.randint(0, 9)
        card_number += str(digit)

        if i % 2 == 0:
            digit *= 2
        if digit > 9:
            digit -= 9

        sum_of_digits += digit
    last_digit = 0
    while not (sum_of_digits + last_digit) % 10 == 0:
        last_digit += 1
    card_number += str(last_digit)
    return card_number


def generate_pin():
    pin = ''
    for i in range(4):
        pin += str(random.randint(0, 9))
    return pin


def create_account():
    card_number = generate_card_number()
    pin = generate_pin()

    # Checks whether generated new number already exists in database
    cur.execute('SELECT number FROM card')
    numbers = cur.fetchall()
    while any(number == card_number for number in numbers):
        card_number = generate_card_number()

    # Creating new account in database
    cur.execute('INSERT INTO card (number, pin) VALUES ({},{})'.format(card_number, pin))
    conn.commit()
    return card_number, pin


# Flow of the program

def start_prompt():
    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit')
    return input()


def login_prompt():
    print('\nEnter your card number:')
    card_number = input()
    print('Enter your PIN')
    pin = input()

    if validate(card_number, pin):
        print('\nYou have successfully logged in!\n')
        logged_in(get_id(card_number))
    else:
        print('\nWrong card number or PIN!\n')
        actions(start_prompt())


def logged_in(account_id):
    print('1. Balance')
    print('2. Add income')
    print('3. Do transfer')
    print('4. Close account')
    print('5. Log out')
    print('0. Exit')
    action = input()
    logged_in_actions(action, account_id)


def actions(action):
    if action == '0':
        print('\nBye!')
        exit()
    elif action == '1':
        card_number, pin = create_account()
        print('\nYour card has been created')
        print('Your card number:')
        print(card_number)
        print('Your card PIN:')
        print(pin + '\n')
        actions(start_prompt())
    elif action == '2':
        login_prompt()


def logged_in_actions(action, account_id):
    if action == '1':
        show_balance(account_id)
    elif action == '2':
        add_income(account_id)
        logged_in(account_id)
    elif action == '3':
        do_transfer(account_id)
        logged_in(account_id)
    elif action == '4':
        close_account(account_id)
        actions(start_prompt())
    elif action == '5':
        print('\nYou have successfully logged out!\n')
        actions(start_prompt())
    elif action == '0':
        actions('0')
    else:
        print('\nOption does not exist. Choose another one\n')
        actions(start_prompt())


# 1
def show_balance(account_id):
    balance = get_balance(account_id)
    print('\nBalance: ' + str(balance) + '\n')
    logged_in(account_id)


# 2
def add_income(account_id):
    print('\nEnter income:')
    income = int(input())
    print('Income was added!\n')
    update_balance(account_id, income)


# 3
# Transfers specified amount from account identified by passed id to an account
# which card number is given
def do_transfer(sender_id):
    print('\nTransfer')
    print('Enter card number:')
    receiver_card_number = input()

    if luhn_check(receiver_card_number):
        if account_exist(receiver_card_number):
            print('Enter how much money you want to transfer:')
            amount = int(input())
            if get_balance(sender_id) >= amount:
                print('Success!')
                update_balance(get_id(receiver_card_number), amount)
                update_balance(sender_id, -amount)
            else:
                print('Not enough money!\n')
        else:
            print('Such a card does not exist.\n')
    else:
        print('Probably you made a mistake in the card number. Please try again!\n')


# 4
# Deletes all records of specified by id account from database
def close_account(account_id):
    cur.execute('DELETE FROM card WHERE id={}'.format(account_id))
    conn.commit()
    print('\nThe account has been closed!\n')


# Helper functions

def update_balance(account_id, amount):
    cur.execute('UPDATE card SET balance = {} WHERE id = {}'.format(amount + get_balance(account_id), account_id))
    conn.commit()


def validate(card_number, pin):
    cur.execute('SELECT number, pin FROM card')
    accounts = cur.fetchall()
    for account in accounts:
        if account[0] == card_number:
            if account[1] == pin:
                return True
    return False


def get_id(card_number):
    cur.execute('SELECT id FROM card WHERE number = {}'.format(card_number))
    return cur.fetchall()[0][0]


def account_exist(card_number):
    cur.execute('SELECT id FROM card WHERE number = {}'.format(card_number))
    if cur.fetchall():
        return True
    else:
        return False


# Checks validity of passed account number
def luhn_check(card_number):
    last_digit = int(card_number[-1])
    card_number = card_number[6:-1]
    sum_of_digits = 8
    for i in range(9):
        digit = int(card_number[i])
        if i % 2 == 0:
            digit *= 2
        if digit > 9:
            digit -= 9
        sum_of_digits += digit
    if (sum_of_digits + last_digit) % 10 == 0:
        return True
    else:
        return False


def get_balance(account_id):
    cur.execute('SELECT balance FROM card WHERE id = {}'.format(account_id))
    return cur.fetchall()[0][0]


# Start of program's execution

def main():
    actions(start_prompt())


main()
