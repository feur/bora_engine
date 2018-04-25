#!/bin/bash

rm -rf bora_local/
cp -a bora/ bora_local/
rm ~/bora_local/python/bittrex/settings.py 
mv ~/bora_local/python/bittrex/livesettings.py bora_local/python/bittrex/settings.py


