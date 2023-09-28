import os
import shutil
from dotenv import load_dotenv
from pykeepass import PyKeePass
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from mega import Mega
from getpass import getpass
from datetime import datetime


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


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
    clear()
    kp_password = getpass("Enter KeePass password: ")
    kp = PyKeePass(keepass_db_path, password=kp_password)

    folders_to_encrypt = get_folders_to_encrypt()
    zip_encryption_entry = get_entry_from_keepass(kp, zip_encryption_entry_title)
    zip_encryption_key = zip_encryption_entry.password.encode('utf-8').ljust(16, b'\0')
    mega_entry = get_entry_from_keepass(kp, mega_entry_title)
    mega_email = mega_entry.username
    mega_password = mega_entry.password

    for index, folder in enumerate(folders_to_encrypt, start=1):
        current_date = datetime.now().strftime("%y%m%d")
        zip_name = os.path.basename(folder) + f"_{current_date}"  
        zip_path = os.path.join(os.getcwd(), zip_name)
        shutil.make_archive(zip_path, 'zip', folder)
        encrypt_file(f"{zip_path}.zip", zip_encryption_key, f"encrypted_{zip_name}.zip")

        mega = Mega()
        m = mega.login(mega_email, mega_password)

        mega_directory = os.getenv('MEGA_DIRECTORY')
        if mega_directory:
            print(f"Uploading to {mega_directory}")
        else:
            directory = input(f"Enter the MEGA directory to upload file {index} to, or press Enter to upload to the main directory: ")
            if directory:
                folder = m.find(directory)
                if folder:
                    m.upload(f"encrypted_{zip_name}.zip", folder[0])
                    print(f"Encrypted file uploaded to {directory}")
                else:
                    print(f"Folder does not exist. Do you want to:")
                    print("1. Upload to main directory")
                    print("2. Try again")
                    choice = input("Enter your choice (1/2): ")
                    if choice == '1':
                        m.upload(f"encrypted_{zip_name}.zip")
                        print(f"Encrypted file uploaded to main directory.")
                    else:
                        continue
            else:
                m.upload(f"encrypted_{zip_name}.zip")
                print(f"Encrypted file uploaded to main directory.")
        print(f"Encrypted file at: encrypted_{zip_name}.zip")
        input("Press enter to continue")
    clear()


def decrypt():
    clear()
    kp_password = getpass("Enter KeePass password: ")
    kp = PyKeePass(keepass_db_path, password=kp_password)

    file_to_decrypt = input("Enter the path of the file to decrypt: ")
    output_path = input("Enter the output path and filename: ")
    if not output_path.endswith('.zip'):
        output_path += '.zip'
    zip_encryption_entry = get_entry_from_keepass(kp, zip_encryption_entry_title)
    zip_encryption_key = zip_encryption_entry.password.encode('utf-8').ljust(16, b'\0')
    decrypt_file(file_to_decrypt, zip_encryption_key, output_path)
    print(f"Decrypted file to {output_path}")
    input("Press enter to continue")
    clear()


def get_folders_to_encrypt():
    folders = os.getenv('FOLDERS_TO_ENCRYPT')
    if not folders:
        print("No folders set to encrypt in .env file.")
        choice = input("Do you want to enter folder paths manually? (y/n): ")
        if choice.lower() == 'y':
            folders = input("Enter folder paths separated by commas: ")
            return folders.split(',')
        else:
            return []
    else:
        return folders.split(',')


def main():
    load_dotenv()
    global keepass_db_path, mega_entry_title, zip_encryption_entry_title
    keepass_db_path = get_keepass_db_path()
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


def get_keepass_db_path():
    db_path = os.getenv('KEEPASS_DATABASE_PATH')
    if not db_path:
        print("KEEPASS_DATABASE_PATH not set in .env file.")
        exit()
    else:
        return db_path


if __name__ == '__main__':
    main()
