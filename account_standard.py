
import re
# (regular expressions)
#----------------------------------------------------------------------------------------
# The funcion checks is the signing username is valid.
# Returns feedback if not
def valid_username(string):
    string = string.strip()
    error_cases = {
        string.isalnum() != True: 'Username must contain only letters and numbers',
        len(string) < 5 or len(string) > 15: 'Username must contain 5 - 14 characters',
        ' ' in string: 'Username should not contain spaces'
    }
    for case in error_cases:
        if case:
            return(True, error_cases[case])
    return False,
#----------------------------------------------------------------------------------------
# The funcion checks is the signing password is valid.
# Returns feedback if not
def valid_key(key):
    key = key.strip()
    error_cases = {
        len(key) < 7 or len(key) > 16:'Password must be 7 - 15 chracters',
        len(re.findall(r'[a-zA-Z]', key)) == 0:'Password must contain letters',
        len(re.findall(r'\d', key)) == 0:'Password must contain digits',
        len(re.findall(r'[@!%$#&*]', key)) == 0: 'Password must contain "@,!,%,$,#,&,*"',
        ' ' in key: 'Password should not contain spaces'
    }
    for case in error_cases:
        if case:
            return(True, error_cases[case])
    else: return False,
#----------------------------------------------------------------------------------------
# The function compares the two passwords.
# Returns feedback if the passwords don't match
def confirm_key(key, confirmed_key):
    if key != confirmed_key:
        return (True, 'The passwords don\'t match')
    else: return False,
#----------------------------------------------------------------------------------------
