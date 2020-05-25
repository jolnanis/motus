#!/bin/bash
# Runs coverage and open html report in firefox

python3 -m coverage run --source=motus -m nose
python3 -m coverage html
firefox htmlcov/index.html