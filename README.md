# Export 1password from command line

## Prerequisites
Having `op` working. Do `op signin` and create `.op.token` in the form like:
```shell
export OP_SESSION_my=XXX
```

where `OP_SESSION_my` comes from `op signin` output.

## Python venv
```shell
python3 -m venv .venv
# or python3.8 -m venv .venv or similar
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
# help
./1password_export.py -h
```

## Running
```shell
make
# or
source .venv/bin/activate
./1password_export.py -o 1password_export.csv
```
## Script options
```shell
$ ./1password_export.py -h

usage: 1password_export.py [-h] [-d] [-u PATH] [-i UUID [UUID ...]] [-g STRING] [-n INT] -o PATH

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Show debug logs (default: False)
  -u PATH, --dumper PATH
                        Dump raw items to the file (default: None)
  -i UUID [UUID ...], --include UUID [UUID ...]
                        Only show output for this UUID (default: None)
  -g STRING, --grouping STRING
                        Folder to be created in LastPass (default: 1password_import)
  -n INT, --max-count INT
                        Max item count to fetch (default: None)
  -o PATH, --output-file PATH
                        Output file (default: None)
```

### How it works
1. get all your 1password vault names
2. for each vault name, export its items
3. for each item in the vault, format it as username, password, note and url, while
   - if there is no url, format the items as a LastPass Secure Note
   - if it is a credit/debit card item, create a special Secure Note recognized by LastPass as a credit/debit card (Start Date is not filled in)
4. dumps formatted items as a CSV file
5. now you can import it from LastPass (Open My Valut > Advanced Options > Import; select "Generic CSV File" as Source and upload it
6. LastPass will offer to "Remove Duplicates", uncheck it (it is safer; you can remove dupes later yourself)

The imported items are in LastPass folder(s) `1password_import :: <vault name>`, e.g. `1password_import :: Personal`. You can easily see all such imported item when you search for `import :: ` (note the spaces) in My LastPass Vault.

