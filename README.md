<h1 align='center'>Chamilo UGA Scraper</h1>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Scraper to download all the material from Chamilo for the UGA. The script downloads all files from the Chamilo platform and creates the required directories on the fly.

## Usage
To run this script, `Python 3.7` or higher is required. The libraries needed are `mechanize` and `beautifulsoup`.

To get the help message run `main.py -h`
```
usage: main.py [-h] [-d DIR] [-u USERNAME] [-p PASSWORD]

UGA Chamilo scraper

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     Directory to download all courses. Defaults to the current directory.
  -u USERNAME, --username USERNAME
						Username
  -p PASSWORD, --password PASSWORD
						Password
```

Both the user and password are needed to login into Chamilo. If they are not provided through as arguments with the `-u` and `-p`, the user will be prompted for them.

> The password is not echoed back for security purposes.

Note that the files will be downloaded to the current directory. To download all documents to another folder pass it through the `-d` argument. The path can be relative or absolute.

## Requirements

### Linux

On most linux systems, Python 3.7 comes pre-installed. If it is not installed, use the package manager to install both `python3` and `pip3`. To install the dependencies:
```
pip install -r requirements.txt
```

## MacOS

To install the dependencies on MacOS:
```
xcode-select --install
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install python3
python3 get-pip.py
pip3 install --user -r requirements.txt
```


## License

This script is under [MIT license](https://github.com/servinagrero/ChamiloUGAScraper/blob/master/LICENSE).
