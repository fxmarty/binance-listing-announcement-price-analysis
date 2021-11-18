# binance-listing-price-analysis
A price analysis of the evolution of crypto price in the minutes and hours following a listing announcement on Binance exchange

Repository architecture:

- cfg: contains config files
- dat: contains data
- lib: contains functions. Python files should be named as `tbx_*.py`
- sandbox: contains test scripts
- Upper folder: contains Python files should be executed, and named as `script_*.py`

Formatter:

- Black with following arguments:
        "python.formatting.blackArgs": [
                "--line-length",
                "120"
            ],
