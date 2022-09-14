import hashlib

# This function returns a list of three hashed passwords (SHA-512) from a list of three passwords and salts
#   (Salts are strings that are appended to passwords before hashing to increase security)
# This function is used in app.py to hash user inputted passwords so they can be checked against the correct passwords
def hash(pwd_inputs, salts): return [hashlib.sha512(pwd_inputs[i].encode('utf-8') + salts[i].encode('utf-8')).hexdigest() for i in range(3)]

# This is here so I can generate new passwords by running this file
if __name__=='__main__':
    salts = ['D90GHL', 'M18XUJ', 'K62QTF']
    pwd_inputs = [input('Please enter a password: ') for _ in range(3)]
    for i in hash(pwd_inputs, salts): print(i)
