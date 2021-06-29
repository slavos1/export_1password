OP_TOKEN_FILE ?= .op.token
# INCLUDE = -i 6zupvatewhupdiywd7iaujv7o4
# INCLUDE = -i h2erriw55nbc2c5mgncfe4wdm4

include ${OP_TOKEN_FILE}

all:
	bash -c 'source .venv/bin/activate && ./1password_export.py -d -o ~/Downloads/1password_export.csv -u .dump.json ${INCLUDE}'

fmt black:
	bash -c 'source .venv/bin/activate && black *.py'

test:
	op get item h2erriw55nbc2c5mgncfe4wdm4|jq -C ''
