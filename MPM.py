import hashlib
import random
from cryptography.fernet import Fernet
import time
import sys
import smtplib
import mysql.connector


# Flow of execution
# PATH 1: new_or_login() -> new_user() -> intro() -> mpass_regemail() -> hashing() -> new_connection() -> table()
# -> password_req() -> (password_generator) -> inserting_values -> password_req() -> passwd_encryption
# -> inserting_values() -> existing_user() -> otp_send -> otp_verify -> verified()
# -> (existing_user or forgot_pass) -> decrypt()
# PATH 2: existing_user() -> otp_send -> otp_verify -> verified() -> decrypt()


def intro():
    print("""Hello New User!
Welcome to Password Manager (●'◡'●)
Can't remember long passwords?
Want a place to store them?
Then we are here to help you in the safest way possible (⌐■_■)
Let's start then...
""")


# Email registration
regmail = input("Enter your email which will be used for verification(please enter a google mail id) :")
intro()

mysql_pass = input("Enter your mysql password :")
db = mysql.connector.connect(host='localhost', user='root', passwd=mysql_pass)
cursor = db.cursor()


def new_or_login():
    print("""
1. Create an account
2. Returning User
Enter choice
""")
    ch = input("(1/2):")
    if ch.startswith('1'):
        new_user()
    elif ch.startswith('2'):
        existing_user()
    else:
        print("Invalid input!")
        print("Restarting the process...")
        new_or_login()


def new_user():
    mast_pass()


def mast_pass():
    global pwd_hashed
    print("""
This software stores all your website addresses, website name, user name and also the main part 'THE PASSWORD'.
Inorder to ensure maximum security, the password manager will be secured by a master-password exclusively known only to 
the user and set according to the user input. The master-password should not be something predictable and it should be 
remembered by you at all times inorder to gain access to the manager. If the master-password is forgotten then you will
receive an email in your registered gmail id containing an OTP through which can be used to reset your master-password.
""")
    print()
    print("""A good master-password should have at least:
i) 8 characters
ii) 1 uppercase letter
iii) 1 digits
iiv) 1 special character
v) No space character
""")
    in_pwd = input("Enter your MASTER-PASSWORD :")
    pwd_hashed = hashing(in_pwd)
    print("Password saved!")
    new_connection()


def new_connection():
    global db_use
    print("""What do you want to do:
1. Create a new database and use it
2. Use existing database
""")
    if input("(1/2)").startswith('1'):
        db_name = input("Enter the name of the new database :")
        create_db = "create database " + db_name
        db_use = "use " + db_name
        cursor.execute(create_db)
        cursor.execute(db_use)
        print("Database changed.")
        table()
    else:
        cursor.execute("show databases")
        for x in cursor:
            print(x)
        db_name = input("Enter the database you want to use :")
        db_use = 'use ' + db_name
        cursor.execute(db_use)
        print('Database changed.')
        table()


def existing_user():
    print("If you have forgotten your master-pass then, enter 'forgot password' when asked to enter 'master-password'")
    master_pwd_check = input("Enter your master-password[you have 3 attempts] :")
    attempts = 3
    if master_pwd_check.lower().startswith('f'):
        forgot_pass()
    else:
        if master_pwd_check == pwd_hashed:
            print("""
An OTP will be sent to your registered email within the next 5 mins. Please enter the OTP carefully."
If OTP is entered incorrectly then, the manager will quit and you will have to restart the password-manager.
""")
            otp_send()
            otp_verify()
            verified()

        else:
            attempts -= 1
            print("Wrong password entered!!!")
            print("You have", attempts, "attempts left!")
            print("""
What do you want to do :
1. Try again
2. Forgot password
""")
            if attempts > 0:
                if input('(1/2):').startswith('1'):
                    existing_user()
                else:
                    print("""An email has been sent to your registered mail id.
Please follow the instructions mentioned in the mail inorder to rest your password.""")
                    forgot_pass()
            else:
                print("You ran out of attempts!")
                print("An email has been sent to your registered mail to reset your password.")
                forgot_pass()


def verified():
    print("""
What do you want to do :
1. Add new account details
2. Retrieve existing account details""")

    if input('(1/2):').startswith('1'):
        inserting_values()
    elif input('(1/2):').startswith('2'):
        print("""
How do you want to retrieve the data :
1. Using URL
2. Using website name
3. Exit
""")
        action = input("(1/2/3):")
        if action.startswith('1'):
            url_in = input("Enter the URL :")
            cursor.execute(db_use)
            display = "select * from " + table_name + " WHERE URL=" + url_in
            cursor.execute(display)
            for x in cursor:
                print(x)
        elif action.startswith('2'):
            web_name = input("Enter the website name(in small letters) :")
            cursor.execute(db_use)
            display = "select * from " + table_name + " WHERE Website=" + web_name
            cursor.execute(display)
            for y in cursor:
                print('URL ---->', y[0])
                print('Website ---->', y[1])
                print('UserName ---->', y[2])
                password = decrypt(web_name)
                print('Password ---->', password)
        elif action.startswith('3'):
            print("Bye Bye...")
            print("See you soon...")
        else:
            print("Wrong choice!")
            print("Lets try this again...")
            print()
            verified()
        ch = input("Do you want to look up info for another site?")
        if ch.lower().startswith('y'):
            verified()
        elif ch.lower().startswith('n'):
            print("Thank-you")
            print("See you next time!")
        else:
            print("Invalid choice!")
            print("Try again...")
            verified()


def table():
    global table_name
    table_name = input("Enter a name for the table :")
    creating_table = "create table " + table_name + " (URL varchar(104),Website varchar(32),UserName varchar(14),Password varchar(203) )"
    cursor.execute(creating_table)
    inserting_values()


def password_req():
    global sec_pass
    print("""
Minimum Requirements for strong password:
i) 15 characters
ii) 1 uppercase letter
iii) 2 digits
iv) 2 special characters
v) Space not accepted as a character
""")
    print()
    print("""
1. Enter password
2. Generate password
""")
    pass_choice = input("(1/2):")
    if pass_choice.startswith('1'):
        test_pass = input("Enter the password you want to use :")
        pass_len = len(test_pass)
        count_char = count_num = count_spec = count_upper = 0
        for i in test_pass:
            if i.isupper():
                count_upper += 1
            elif i.isdigit():
                count_num += 1
            elif i.isalpha():
                count_char += 1
            elif i.isspace():
                print("Error: You have entered a space character in your password which is not acceptable :)")
                print("Let's start from password once more...")
                time.sleep(2)
                print()
                password_req()

            else:
                count_spec += 1

        if pass_len < 15:
            print("""
Add more characters to make it a strong password!
Use more letters, digits or special characters to bring the length of the password up to 15 (at least).
Don't worry you don't need to remember it, we will do that for you :)
Let's try this again.
Let's start from password once more...
""")
            time.sleep(2)
            print()
            password_req()

        else:
            if count_upper > 0 and count_num > 1 and count_spec > 1:
                sec_pass = test_pass
                print("All requirements met.")
                print("Is", sec_pass, "your final choice of password ?")
                if input('(y/n) :').lower().startswith('y'):
                    print('Password set!')
                    return sec_pass
                else:
                    print("Let's start from password once more...")
                    password_req()
            else:
                print("Insufficient number of upper case letter or numbers or special characters. ")
                print("Restarting password setting in 5 secs...")
                time.sleep(5)
                password_req()

    elif pass_choice.startswith('2'):
        gen_pass = password_generator()
        return gen_pass

    else:
        print("Invalid input!")
        print("Restarting password setting in 3 secs...")
        time.sleep(3)
        password_req()


def inserting_values():
    global encrypted_pwd
    url = input("Enter the URL of the website(if you want to skip this enter 'skip') :")
    website = input("Enter the name of the website(in small letters) :")
    user_name = input("Enter the user name to be used of the account :")
    acc_pwd = password_req()
    encrypted_pwd = passwd_encryption(acc_pwd)
    # print(encrypted_pwd)
    store_pwd = encrypted_pwd
    insert_values = "INSERT INTO " + table_name + " (URL, Website, UserName, Password) " + "VALUES (" + "'" + url + "'" + ", " + "'" + website + "'" + ", " + "'" + user_name + "'" + ", " + "'" + encrypted_pwd + "'" + ")"
    cursor.execute(insert_values)
    db.commit()
    print("Data has been successfully added to the database!")


def passwd_encryption(sec_passwd):
    global encryption
    global encrypt_str_pass
    global encrypted_pass
    key = Fernet.generate_key()
    encrypto = Fernet(key)
    encrypted_pass = encrypto.encrypt(sec_passwd.encode())
    encrypt_str_pass = str(encrypted_pass, 'utf8')
    return encrypt_str_pass


def hashing(pw):
    return hashlib.sha256(str.encode(pw)).hexdigest()


def decrypt(web_name1):
    decrypted_pass = encryption.decrypt(encrypted_pass)
    return str(decrypted_pass, 'utf8')
