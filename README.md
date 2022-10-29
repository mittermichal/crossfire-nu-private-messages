Script to download private messages from https://crossfire.nu
Messages will be saved as json file.

### Installation
- install python 3
- install BeautifulSoup4: `pip install beautifulsoup4`
- run the script: `python crossfire-nu-private-messages.py`

#### Known issues:

- getpass doesn't seem to work in MinGW, you can edit line where password is set instead: `password = <your_cf_password>`
