import os
import shutil
from dotenv import load_dotenv
from pykeepass import PyKeePass
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from mega import Mega
from getpass import getpass


def get_entry_from_keepass(kp, entry_title):
    entry = kp.find_entries(title=entry_title, first=True)
    return entry


def encrypt_file(file_path, key, output_path):
    block_size = 16
    with open(file_path, 'rb') as f:
        plaintext = f.read()
    iv = get_random_bytes(block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(pad(plaintext, block_size))
    with open(output_path, 'wb') as f:
        f.write(iv + ciphertext)

def decrypt_file(file_path, key, output_path):
    block_size = 16
    with open(file_path, 'rb') as f:
        iv = f.read(block_size)
        ciphertext = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = unpad(cipher.decrypt(ciphertext), block_size)
    with open(output_path, 'wb') as f:
        f.write(plaintext)

def encrypt_and_upload():
    kp_password = getpass("Enter KeePass password: ") 
    kp = PyKeePass(keepass_db_path, password=kp_password)
    
    folders_to_encrypt = os.getenv('FOLDERS_TO_ENCRYPT').split(',')
    zip_encryption_entry = get_entry_from_keepass(kp, zip_encryption_entry_title)
    zip_encryption_key = zip_encryption_entry.password.encode('utf-8').ljust(16, b'\0') 
    mega_entry = get_entry_from_keepass(kp, mega_entry_title)
    mega_email = mega_entry.username
    mega_password = mega_entry.password
    
    for folder in folders_to_encrypt:
        zip_name = os.path.basename(folder) + ".zip"
        shutil.make_archive(os.path.basename(folder), 'zip', folder)
        encrypt_file(zip_name, zip_encryption_key, f"encrypted_{zip_name}")
        mega = Mega()
        m = mega.login(mega_email, mega_password)
        m.upload(f"encrypted_{zip_name}")

def decrypt():
    kp_password = getpass("Enter KeePass password: ") 
    kp = PyKeePass(keepass_db_path, password=kp_password)
    
    file_to_decrypt = input("Enter the path of the file to decrypt: ")
    output_path = input("Enter the output path and filename: ")
    zip_encryption_entry = get_entry_from_keepass(kp, zip_encryption_entry_title)
    zip_encryption_key = zip_encryption_entry.password.encode('utf-8').ljust(16, b'\0')
    decrypt_file(file_to_decrypt, zip_encryption_key, output_path)

def main():
    load_dotenv()
    global keepass_db_path, mega_entry_title, zip_encryption_entry_title
    keepass_db_path = os.getenv('KEEPASS_DATABASE_PATH')
    mega_entry_title = os.getenv('MEGA_ENTRY_TITLE')
    zip_encryption_entry_title = os.getenv('ZIP_ENCRYPTION_ENTRY_TITLE')
    
    while True:
        print("1. Encrypt and Upload")
        print("2. Decrypt")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            encrypt_and_upload()
        elif choice == '2':
            decrypt()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
