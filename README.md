# NWN assets

Version: 89.8193.37-16

This repository contains all the 2da, nss, dlg, and blueprint assets of the Neverwinter Nights game.

It is capable of creating a hak with the hardcoded translations of the blueprints and dialogs.

For Polish, and because of different codepages, the diacritics are removed.


## Usage

The following repository uses shell script and python to generate translations.

In order to update the repository to your NWN version, run the following, optionally passing the path of your `Neverwinter Nights`:

~~~
./bin/update-from-nwn-directory
# or
./bin/update-from-nwn-directory "$HOME/Neverwinter Nights"
~~~ 

Issues may arise if using a directory with spaces. In such a case, using symlinks can solve the issues.


In order to add all translations, run the translate script after having created a python virtual environment:

~~~
# Note: python3 may be called python on some systems
virtualenv .venv
# or
python3 -mvenv .venv

# Activate the environment:
source .venv/bin/activate

# Install the dependencies:
pip install -r requirements.txt

# Run translations script
./bin/translate.py
~~~

In order to create the hak files:
~~~
./bin/create-hak.sh
~~~
