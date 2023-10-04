import os
import shutil
import tempfile
from dotenv import load_dotenv
from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from mega import Mega
from getpass import getpass
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tkinter import Tk, filedialog


def authenticate_google_drive():
    google_drive_credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH')
    
    if not os.path.exists(google_drive_credentials_path):
        print("g-drive credentials not found.")
        choice = input("Continue with explorer to find file? [Y/n]: ").strip().lower()
        if not choice or choice == 'y':
            google_drive_credentials_path = open_file_explorer_to_select_file()
            if not google_drive_credentials_path or not os.path.exists(google_drive_credentials_path):
                print("File not selected or invalid file. Exiting...")
                exit()

    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(google_drive_credentials_path)
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)


def open_file_explorer_to_select_file():
    """ This function will open a file explorer and return the selected file path """
    root = Tk()
    root.withdraw() 
    file_path = filedialog.askopenfilename(title="Select g-drive credentials file", filetypes=[("JSON Files", "*.json")])
    return file_path


def upload_to_google_drive(file_path, folder_name=None):
    drive = authenticate_google_drive()
    file = drive.CreateFile({'title': os.path.basename(file_path)})
    file.SetContentFile(file_path)
    file.Upload()
    print(f"File uploaded to Google Drive with ID {file['id']}")


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


def encrypt_and_upload():
    clear()
    try:
        kp_password = getpass("Enter KeePass password: ")
        kp = PyKeePass(keepass_db_path, password=kp_password)

        folders_to_encrypt = get_folders_to_encrypt()
        zip_encryption_entry = get_entry_from_keepass(kp, zip_encryption_entry_title)
        zip_encryption_key = zip_encryption_entry.password.encode('utf-8').ljust(16, b'\0')
        mega_entry = get_entry_from_keepass(kp, mega_entry_title)
        mega_email = mega_entry.username
        mega_password = mega_entry.password

        script_dir = os.path.dirname(os.path.abspath(__file__))
        with tempfile.TemporaryDirectory(dir=script_dir) as tempdir:
            for index, folder in enumerate(folders_to_encrypt, start=1):
                current_date = datetime.now().strftime("%y%m%d")
                zip_name = os.path.basename(folder) + f"_{current_date}"
                zip_path = os.path.join(tempdir, zip_name)
                shutil.make_archive(zip_path, 'zip', folder)
                encrypt_file(f"{zip_path}.zip", zip_encryption_key, f"{tempdir}/encrypted_{zip_name}.zip")

                print("1. Upload to MEGA")
                print("2. Upload to Google Drive")
                choice = input("Enter your choice: ")  

                if choice == '1': 
                    mega = Mega()
                    m = mega.login(mega_email, mega_password)

                    mega_directory = os.getenv('MEGA_DIRECTORY')
                    if mega_directory:
                        print(f"Uploading to {mega_directory}")
                        folder = m.find(mega_directory, exclude_deleted=True)
                        if folder:
                            m.upload(f"{tempdir}/encrypted_{zip_name}.zip", folder[0])
                            print(f"Encrypted file uploaded to {mega_directory}")
                        else:
                            print(f"Folder {mega_directory} does not exist. Uploading to main directory.")
                            m.upload(f"{tempdir}/encrypted_{zip_name}.zip")
                    else:
                        m.upload(f"{tempdir}/encrypted_{zip_name}.zip")
                        print(f"Encrypted file uploaded to main directory.")
                    print(f"Encrypted file at: {tempdir}/encrypted_{zip_name}.zip")
                    input("Press enter to continue")
                    break
                elif choice == '2':
                    upload_to_google_drive(f"{tempdir}/encrypted_{zip_name}.zip")
                    break
                else:
                    print("Invalid choice.")
    except (CredentialsError, IOError):
        print("Error: Incorrect KeePass password or database not found.")
        input("Press enter to continue...")
        encrypt_and_upload()
    main()


def decrypt():
    try:
        clear()
        kp_password = getpass("Enter KeePass password: ")
        kp = PyKeePass(keepass_db_path, password=kp_password)

        file_to_decrypt = input("Enter the path of the file to decrypt: ")
        if not file_to_decrypt:
            print("Error: No file path provided.")
            return
        elif not os.path.exists(file_to_decrypt):
            print("Error: File not found.")
            return
        choice = input("Decrypt to the same file? [Y/n]: ").strip().lower()
        if choice not in ['', 'y', 'n']:
            print("Error: Invalid response. Please enter Y or N.")
            return

        if not choice or choice == 'y':
            zip_encryption_entry = get_entry_from_keepass(kp, zip_encryption_entry_title)
            zip_encryption_key = zip_encryption_entry.password.encode('utf-8').ljust(16, b'\0')
            success = decrypt_file(file_to_decrypt, zip_encryption_key, file_to_decrypt)
            if success:
                print(f"Decrypted file to {file_to_decrypt}")
        else:
            output_path = input("Enter the output path and filename: ")
            if not output_path.endswith('.zip'):
                output_path += '.zip'
            zip_encryption_entry = get_entry_from_keepass(kp, zip_encryption_entry_title)
            zip_encryption_key = zip_encryption_entry.password.encode('utf-8').ljust(16, b'\0')
            success = decrypt_file(file_to_decrypt, zip_encryption_key, output_path)
            if success:
                print(f"Decrypted file to {output_path}")

        input("Press enter to continue...")
        clear()
    except (CredentialsError, IOError):
        print("Error: Incorrect KeePass password or database not found.")
        input("Press enter to continue...")
        decrypt()



def decrypt_file(file_path, key, output_path):
    block_size = 16
    try:
        with open(file_path, 'rb') as f:
            iv = f.read(block_size)
            ciphertext = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        plaintext = unpad(cipher.decrypt(ciphertext), block_size)
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        return True  # Successfully decrypted the file
    except ValueError as e:
        if str(e) == "Data must be padded to %d byte boundary in CBC mode" % block_size:
            print("Error: The file you are trying to decrypt seems to be already decrypted or is not in the correct format.")
        else:
            print("An error occurred during decryption:", e)
        return False  # An error occurred during decryption



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
    clear()
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
