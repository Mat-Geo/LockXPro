import hashlib
import random
from cryptography.fernet import Fernet
import time
# import sys
import smtplib
import mysql.connector


# Flow of execution
# PATH 1: new_or_login() -> new_user() -> intro() -> mast_pass() -> hashing() -> new_connection() -> table()
# -> password_req() -> (password_generator) -> inserting_values -> password_req() -> passwd_encryption
# -> inserting_values() -> existing_user() -> otp_send -> otp_verify -> verified()
# -> (existing_user or forgot_pass) -> decrypt()
# PATH 2: existing_user() -> otp_send -> otp_verify -> verified() -> decrypt()


def intro():
    print("""Hello User!
Welcome to Password Manager (●'◡'●)
Can't remember long passwords?
Want a place to store them?
Then we are here to help you in the safest way possible (⌐■_■)
Let's start then...
""")


regmail = ''
intro()

mysql_pass = input("Enter your mysql password :")
db = mysql.connector.connect(host='localhost', user='root', passwd=mysql_pass)
cursor = db.cursor()


def new_or_login():  # provides option to either CREATE AN ACCOUNT OR LOGIN TO AN EXISTING ACCOUNT
    print("""
1. Create an account
2. Returning User
Enter choice
""")
    ch = input("(1/2):")
    if ch.startswith('1'):
        new_user()  # Navigates to Creating an account for new user ( moves to line 55)
    elif ch.startswith('2'):
        existing_user(attempts)  # Navigates to verification of existing user (moves to line 113)
    else:
        print("Invalid input!")
        print("Restarting the process...")
        time.sleep(5)
        new_or_login()  # Restarts this process as an invalid input was provided (moves to line 37)


def new_user():
    mast_pass()  # Asks user to set his personal master-password which will act as his private key and
    # enable him to gain access to the Manager (moves to line 60)
    new_connection()  # Next, the software creates a database and table to the hold the details of
    # various accounts of the user (moves to line 88)


pwd_hashed = ''


def mast_pass():
    global pwd_hashed
    time.sleep(5)
    print("""
This software stores all your website addresses, website name, user name and also the main part 'THE PASSWORD'.
Inorder to ensure maximum security, the password manager will be secured by a master-password exclusively known only to 
the user and set according to the user input. The master-password should not be something predictable and it should be 
remembered by you at all times inorder to gain access to the manager. If the master-password is forgotten then you will
receive an email in your registered gmail id containing an OTP through which can be used to reset your master-password.
""")
    print()
    time.sleep(3)
    print("""A good master-password should have at least:
i) 8 characters
ii) 1 uppercase letter
iii) 1 digits
iiv) 1 special character
v) No space character
""")
    time.sleep(3)
    in_pwd = input("Enter your MASTER-PASSWORD :")
    pwd_hashed = hashing(
        in_pwd)  # The master-password gets hashed and returned back to the variable (moves to line 316)
    time.sleep(2)
    print("Password saved!")  # The master-password has been saved in hash format and it cannot be decoded at all


db_use = ''
encrypto = ''


def new_connection():
    global db_use
    global encrypto
    global regmail
    print("""What do you want to do:
1. Create a new database and use it
2. Use existing database
""")
    key = Fernet.generate_key()
    encrypto = Fernet(key)
    # Email registration
    regmail = input("Enter your email which will be used for verification(please enter a google mail id) :")

    if input("(1/2)").startswith('1'):
        db_name = input("Enter the name of the new database :")  # Asks the user to create a new database
        create_db = "create database " + db_name
        db_use = "use " + db_name
        cursor.execute(create_db)
        cursor.execute(db_use)
        print("Database changed.")  # The database is changed from default to the database given by the user
        table()  # Navigates to configuration of table in the chosen database (moves to line 205)
    else:
        cursor.execute("show databases")
        for x in cursor:
            print(x)
        db_name = input("Enter the database you want to use :")  # Enables user to make use of already existing database
        db_use = 'use ' + db_name
        cursor.execute(db_use)
        print('Database changed.')  # Database changed from default to that chosen by user
        table()  # Navigates to config of table existing in the chosen database (moves to line 205)


attempts = 2


def existing_user(attempts_left):
    print("If you have forgotten your master-pass then, enter 'forgot password' when asked to enter 'master-password'")
    # Verifies the user using his master-password
    master_pwd_input = input("Enter your master-password :")
    master_pwd_check = hashing(master_pwd_input)
    if master_pwd_check.lower().startswith('f'):  # If user has forgotten his password then an email will be sent to
        forgot_pass()  # the registered mail id containing instructions to reset his password

    else:

        if master_pwd_check == pwd_hashed:  # Master-password is matched and first step of verification is over
            print("""
An OTP will be sent to your registered email within the next 5 mins. Please enter the OTP carefully."
If OTP is entered incorrectly then, the manager will quit and you will have to restart the password-manager.
""")
            time.sleep(3)
            otp_send()  # Initialisation of sending an OTP takes place(moves to line 329)
            otp_verify()  # OTP verification takes place(moves to line 346)
            verified()  # Second verification is also success and user has been granted access to data(moves to line 155)

        else:
            attempts_left -= 1
            print("Wrong password entered!!!")
            print("You have", attempts, "attempts left!")
            print("""
What do you want to do :
1. Try again
2. Forgot password
""")
            if input('(1/2):').startswith('1'):
                if attempts_left > 0:
                    time.sleep(2)
                    existing_user(attempts_left)  # Reinitialize the verification process(moves to line 114)
                else:
                    print("You ran out of attempts!")
                    print("An email has been sent to your registered mail to reset your password.")
                    forgot_pass()  # User has incorrectly entered master-password and an email has been sent to
                    # reset the password (moves to line 382)

            else:
                print("""An email has been sent to your registered mail id.
                Please follow the instructions mentioned in the mail inorder to rest your password.""")
                forgot_pass()  # User has forgotten password and an email has been sent to registered mail
                # with OTP which can be used to reset master-password (moves to line 382)


def verified():
    print("""
What do you want to do :
1. Add new account details
2. Retrieve existing account details""")

    if input('(1/2):').startswith('1'):
        inserting_values()  # Navigates to function to add details of new account (moves to line 296)

    elif input('(1/2):').startswith('2'):
        print("""
How do you want to retrieve the data :
1. Using URL
2. Using website name
3. Exit
""")
        time.sleep(2)
        action = input("(1/2/3):")
        if action.startswith('1'):
            url_in = input("Enter the URL :")  # Fetches the data corresponding to URL entered by user
            cursor.execute(db_use)
            display = "select * from " + table_name + " WHERE URL=" + "'" + url_in + "'"
            cursor.execute(display)
            for x in cursor:
                print('URL ---->', x[0])
                print('Website ---->', x[1])
                print('UserName ---->', x[2])
                password = decrypt(x[3])
                print('Password ---->', password)  # Prints the fetched data along with the decrypted password
        elif action.startswith('2'):
            web_name = input("Enter the website name(in small letters) :")  # Searches and retrieves the data
            cursor.execute(db_use)  # corresponding to the website name
            display = "select * from " + table_name + " WHERE Website=" + "'" + web_name + "'"
            cursor.execute(display)
            for y in cursor:
                print('URL ---->', y[0])
                print('Website ---->', y[1])
                print('UserName ---->', y[2])
                password = decrypt(y[3])
                print('Password ---->', password)  # # Prints the retrieved data along with the decrypted password

        elif action.startswith('3'):
            print("Bye Bye...")
            print("See you soon...")  # exits the program

        else:
            print("Wrong choice!")
            print("Lets try this again...")
            print()
            verified()  # Restarts the process as a wrong choice other than (1/2/3) was entered(moves to line 157)

        ch = input("Do you want to look up info for another site?")  # Provides an option to look up data of another
        if ch.lower().startswith('y'):  # account as well
            verified()  # initiates the same process to provide data of another account(moves to line 157)

        elif ch.lower().startswith('n'):
            print("Thank-you")  # exits the program
            print("See you next time!")

        else:
            print("Invalid choice!")
            print("Try again...")
            verified()  # restarts the process as an invalid input was provided by the user (moves to line 157)


table_name = ''


def table():
    global table_name
    table_name = input("Enter a name for the table :")  # creates a table defined by user
    creating_table = "create table " + table_name + " (URL varchar(104),Website varchar(32),UserName varchar(14),Password varchar(203) )"
    cursor.execute(creating_table)
    inserting_values()  # Navigates to inserting functions next


sec_pass = ''


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
    time.sleep(3)
    print("""
1. Enter password
2. Generate password
""")
    pass_choice = input("(1/2):")
    if pass_choice.startswith('1'):
        test_pass = input("Enter the password you want to use :")  # takes a password entered by user and verifies if
        pass_len = len(test_pass)  # satisfies all requirements to ensure safety
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
                time.sleep(3)
                print()
                password_req()  # restarts the process as the password included space character(moves to line 229)

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
            password_req()  # re-initiates the process as the password length requirement was not met(moves to line 229)

        else:
            if count_upper > 0 and count_num > 1 and count_spec > 1:
                sec_pass = test_pass
                print("All requirements met.")
                print("Is", sec_pass, "your final choice of password ?")
                if input('(y/n) :').lower().startswith('y'):  # asks user to confirm entered password
                    print('Password set!')  # password has been set
                    return sec_pass
                else:
                    print("Let's start from password once more...")
                    time.sleep(3)
                    password_req()  # restarts process as user was not satisfied with the password entered and wanted
                    # to re-enter the password(moves to line 229)
            else:
                print("Insufficient number of upper case letter or numbers or special characters. ")
                print("Restarting password setting ...")
                time.sleep(4)
                password_req()  # restarts the process few requirements were not fulfilled(moves to line 229)

    elif pass_choice.startswith('2'):
        sec_pwd = password_generator()  # automatically generates a password(moves to line 372)
        return sec_pwd

    else:
        print("Invalid input!")
        print("Restarting password setting in 3 secs...")
        time.sleep(3)
        password_req()  # restarts the process as an invalid input was given by user(moves to line 229)


encrypted_pwd = ''


def inserting_values():
    global encrypted_pwd
    url = input("Enter the URL of the website(if you want to skip this enter 'skip') :")
    website = input("Enter the name of the website(in small letters) :")
    user_name = input("Enter the user name to be used of the account :")
    acc_pwd = password_req()  # asks user to create password for his account(moves to line 229)
    encrypted_pwd = passwd_encryption(acc_pwd)  # encrypts the password chosen by user(moves to line 323)

    insert_values = "INSERT INTO " + table_name + " (URL, Website, UserName, Password) " + "VALUES (" + "'" + url + "'" + ", " + "'" + website + "'" + ", " + "'" + user_name + "'" + ", " + "'" + encrypted_pwd + "'" + ")"
    cursor.execute(insert_values)
    db.commit()
    print("Data has been successfully added to the table!")  # data has been inserted into the table


encrypt_str_pass = ''


def passwd_encryption(sec_passwd):
    global encrypt_str_pass

    encrypted_pass = encrypto.encrypt(sec_passwd.encode())
    encrypt_str_pass = str(encrypted_pass, 'utf8')  # converts the encrypted password from bytes to string
    return encrypt_str_pass


def hashing(pw):
    return hashlib.sha256(str.encode(pw)).hexdigest()  # hashes the master-password


def decrypt(display_pass):
    decrypted_pass = encrypto.decrypt(display_pass)  # decrypts the password of an account for the user to see
    return str(decrypted_pass, 'utf8')


OTP = ''


def otp_send():
    global OTP
    otp = []

    for i in range(4):
        code = str(random.randint(0, 9))
        otp.append(code)
    random.shuffle(otp)  # offers more entropy to the generated password
    OTP1 = ''.join(otp)  # generates a random OTP
    OTP = "Your OTP is - " + OTP1
    email = "mypersonalpass21@gmail.com"
    remail = input("Enter your registered email :")
    with smtplib.SMTP("smtp.gmail.com", 587)as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(email, "uwtbywvqjghwrodf")
        smtp.sendmail(email, remail, OTP)


def otp_verify():
    print(OTP)
    otp_check = input("Enter OTP {____} :")

    if otp_check == OTP:
        print("Verified!")  # verifies the OTP sent to the mail
        return True

    else:
        print("Restart the program and try again!!")
        print(
            "Quiting Program...")  # if user fails in verifying the OTP then the program shuts down and has to be restarted
        # sys.exit()
        otp_verify()


def password_generator():
    lo_alphas = "abcdefghijklmnopqrstuvwxyz"
    up_alphas = lo_alphas.upper()
    alphas = lo_alphas + up_alphas
    nums = "0123456789"
    symbs = "!@#$%^&*~?+"
    L1 = L2 = L3 = []

    for i in range(11):
        a = random.choice(alphas)
        L1.append(a)

    for j in range(2):
        b = random.choice(nums)
        L2.append(b)

    for k in range(2):
        c = random.choice(symbs)
        L3.append(c)

    L = L1 + L2 + L3
    random.shuffle(L)  # offers more entropy
    rand_pass = ''.join(L)  # generates a random 15 character password with a mix of both upper & lower
    return rand_pass  # case letters, numbers and special symbols shuffled randomly


def forgot_pass():
    print()
    otp_send()
    print("An email has been sent to", regmail, " with an OTP!")  # sends a mail to reset password by verifying OTP
    otp_verify()
    mast_pass()  # resets the master-password


def queries():
    print("""If you encounter any issue(s) related to the working of the program 
or if you have any queries please don't hesitate to contact our help desk via email.
Please send an email or contact us through github.com stating the issue or query in detail and our team will get back to you soon.
""")
    time.sleep(6)
    print()
    print("""Contact Us: 
email: mypersonalpass21@gmail.com")
github: https://github.com/Soul-Breaker/My-Pass-Manager
""")
    print("Thank-you")


program_initiate = new_or_login()
# otp_send()
query_or_issue = input(""" If everything went perfectly and if you are satisfied with our performance please enter 'y'
OR
If you want to raise a query or report an issue enter 'qi'
""")  # takes a feedback from the user
time.sleep(3)

if query_or_issue.lower().startswith('y'):
    print("It was our pleasure serving you 😇😇😇!")

elif query_or_issue.lower().startswith('q'):
    print()  # enables user to raise errors, provide feedbacks and suggestions and, to contact us regarding
    queries()  # any queries.

