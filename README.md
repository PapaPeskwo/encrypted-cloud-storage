# Encrypted Cloud Storage

This Python script enables you to encrypt directories and upload them to a MEGA.nz cloud storage account. It utilizes a KeePass database to securely store and retrieve the encryption and MEGA account credentials, ensuring enhanced security for your sensitive data.

### KeePass Download:
- [KeePassXC Download](https://keepassxc.org/download/)
- [KeePass Download](https://keepass.info/download.html)

## Features

- Encrypt directories and upload them to MEGA.nz cloud storage.
- Option to decrypt the files back from the cloud.
- Directory paths and KeePass database paths can be entered manually if not set in .env file.
- Allows user to upload to a specific folder in MEGA.nz cloud storage.

## Prerequisites

Ensure you have the following Python libraries installed:
- pykeepass
- Crypto
- python-dotenv
- mega.py

You can install them using:

```bash
pip install -r requirements.txt
```
or:
```bash
pip install pykeepass pycryptodome python-dotenv mega.py
```

## Usage

1. Set your environment variables in a .env file in the same directory as the script. Example:

```plaintext
FOLDERS_TO_ENCRYPT=/path/to/folder1,/path/to/folder2
KEEPASS_DATABASE_PATH=/path/to/keepass.kdbx
MEGA_ENTRY_TITLE=MEGA
ZIP_ENCRYPTION_ENTRY_TITLE=ZIP
MEGA_DIRECTORY=path/to/folder
```

2. Run the script:

```bash
python encrypted_cloud_storage.py
```

3. Follow the on-screen prompts to encrypt and upload, or decrypt your directories.

### Encrypt and Upload:

- Enter 1 to choose the Encrypt and Upload option.
- Enter your KeePass password when prompted.
- Enter the MEGA directory to upload to or press Enter to upload to the main directory.
- The script will inform you about the encryption and upload status.

### Decrypt:

- Enter 2 to choose the Decrypt option.
- Enter your KeePass password when prompted.
- Enter the path of the file to decrypt and the output path and filename.
- The script will inform you about the decryption status.

#### Exit:

- Enter 3 to exit the script.

## Note

- If you are using paths in the script, make sure to use double backslashes (\\) or single forward slashes (/) to avoid errors, e.g., F:\\temp\\test_encrypt or F:/temp/test_encrypt.

## Troubleshooting

- Ensure your .env file is correctly configured with the appropriate paths and titles.
- Ensure your Python environment has the necessary libraries installed.
- Check your internet connection as the script requires access to MEGA.nz for uploading and downloading files.

If you encounter any issues or have suggestions for improvement, feel free to open an issue or make a pull request :))))