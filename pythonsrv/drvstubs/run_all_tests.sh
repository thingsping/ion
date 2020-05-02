#!/bin/bash
python3 createcredentials.py
echo "Register all known devices"
python3 test_utility.py -ra
echo "Run register tests"
python3 test_utility.py -d regtests
echo "Run Advertisement tests"
python3 test_utility.py -d adtests
echo "Run Publish tests"
python3 test_utility.py -d pubtests
echo "Create subscriptions"
python3 createsubscriptions.py
echo "Create events for subscriptions"
python3 test_utility.py -f subscribes/subscribe_entities
echo "Run event action without deleting database"
python3 test_utility.py -nd -d subscribes_nodeldb
echo "Run event action tests for those that need a clean db before. "
python3 test_utility.py -d subscribes

