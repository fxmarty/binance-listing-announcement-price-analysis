# binance-listing-price-analysis
A price analysis of the evolution of crypto price in the minutes and hours following a listing announcement on Binance exchange

On devrait utiliser nulle part ailleurs que dans `config.py` des paths persos.

Repository architecture:

- cfg: contains config files
- dat: contains data
- lib: contains functions. Python files should be named as "tbx_xxx_functions.py" of "tbx_xxx_utils.py"
- sandbox: contains test scripts
- src: contains main scripts to execute. Python files should be named as "script_do_something.py"

Formatter:

- Black with following arguments:
        "python.formatting.blackArgs": [
                "--line-length",
                "120"
            ],