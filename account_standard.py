import re

#----------------------------------------------------------------------------------------
def valid_username(string):
    string = string.strip()
    error_cases = {
        string.isalnum() != True: 'Username must contain only letters and numbers',
        len(string) < 5 : 'Username must contain at least 5 characters',
        ' ' in string: 'Username should not contain spaces'
    }
    for case in error_cases:
        if case:
            return(True, error_cases[case] )
    return False,

#----------------------------------------------------------------------------------------
def valid_key(key):
    key = key.strip()
    error_cases = {
        len(key) < 7:'Password must be at list 7 characters long',
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
def confirm_key(key, confirmed_key):
    if key != confirmed_key:
        return (True, 'The passwords don\'t match')
    else: return False,
#----------------------------------------------------------------------------------------
