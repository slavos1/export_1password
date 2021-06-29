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
```

### How it works
1. get all your 1password vaults
2. for each vault do export
3. for each item in the vault format it as username, password, note and url
   - if there is no url, format se a Secure Note
   - if it is a credit/debit card, create a special Secure Note for LastPass to recognize it as credit/debit card (Start Date is not filled in)
