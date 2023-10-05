# Encrypted Cloud Storage

This Python script enables you to encrypt directories and upload them to either a MEGA.nz cloud storage account or Google Drive. It utilizes a KeePass database to securely store and retrieve the encryption and account credentials, ensuring enhanced security for your sensitive data.

### KeePass Download:
- [KeePassXC Download](https://keepassxc.org/download/)
- [KeePass Download](https://keepass.info/download.html)

## Features

- Encrypt directories and upload them to MEGA.nz or Google Drive cloud storage.
- Option to decrypt the files back from the cloud.
- Directory paths and KeePass database paths can be entered manually if not set in .env file.
- Allows user to upload to a specific folder in MEGA.nz or Google Drive cloud storage.

## Prerequisites

Ensure you have the following Python libraries installed:

- pykeepass 
- mega.py 
- python-dotenv
- pycryptodome
- PyDrive

You can install them using:

```bash
pip install -r requirements.txt
```

## Usage

1. Set your environment variables in a .env file in the same directory as the script. Example:

```plaintext
FOLDERS_TO_ENCRYPT=/path/to/folder1,/path/to/folder2
KEEPASS_DATABASE_PATH=/path/to/keepass.kdbx
MEGA_ENTRY_TITLE=MEGA
ZIP_ENCRYPTION_ENTRY_TITLE=ZIP
MEGA_DIRECTORY=path/to/folder
GOOGLE_DRIVE_CREDENTIALS_PATH=path/to/your/client_secrets.json
```

2. Run the script:

```bash
python encrypted_cloud_storage.py
```

3.Follow the on-screen prompts to encrypt and upload, or decrypt your directories.

### Flags
The script can be ran with the `-i` flag to ignore the .env file and let the user manually enter everything that's needed.

#### Usage
```bash
python encrypted_cloud_storage.py -i
```

### Encrypt and Upload:

- Enter 1 to choose the Encrypt and Upload option.
- Enter your KeePass password when prompted.
- Choose the cloud storage option (MEGA.nz or Google Drive).
- Enter the directory to upload to or press Enter to upload to the main directory.
- The script will inform you about the encryption and upload status.

### Decrypt:

- Enter 2 to choose the Decrypt option.
- Enter your KeePass password when prompted.
- Enter the path of the file to decrypt and the output path and filename.
- The script will inform you about the decryption status.

### Exit:

- Enter 3 to exit the script.

## Setting Up Google Drive with OAuth

Watch this video: https://youtu.be/bkZns_VOB6I?si=yRmqiN9Z90ewF6nV&t=91
or follow these steps:

1. Google Cloud Console: Start by creating a project in the Google Cloud Console.

2. Enable Google Drive API:
    - In the left-hand sidebar, navigate to the API & Services > Library.
    - Search for "Google Drive API" and select it.
    - Click "Enable".

3. OAuth Consent:
    - Once the API is enabled, navigate to the OAuth consent screen.
    - Click on "OAuth consent".
    - Fill in the required fields.
    - Click "Save and Continue".

4. Scopes:
    - On the next screen, click on "Add or remove scopes".
    - Add the scope: https://www.googleapis.com/auth/drive.file.
    - Click "Save and Continue".

5. Not Verified Warning:
    - If you encounter a "Not verified" warning during this process:
        - Click on "Advanced".
        - Proceed by clicking on "Continue".

6. Generate Credentials:
    - Follow the rest of the OAuth setup process to generate your credentials file.

## Note

- If you are using paths in the script, make sure to use double backslashes (\) or single forward slashes (/) to avoid errors, e.g., F:\temp\test_encrypt or F:/temp/test_encrypt.

## Troubleshooting

- Ensure your .env file is correctly configured with the appropriate paths and titles.
- Ensure your Python environment has the necessary libraries installed.
- Check your internet connection as the script requires access to MEGA.nz or Google Drive for uploading and downloading files.

If you encounter any issues or have suggestions for improvement, feel free to open an issue or make a pull request :))))
