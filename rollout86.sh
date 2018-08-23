#!/bin/bash

cd bora/
git fetch
git pull

cd

rm -rf Fink
cp -a bora/x86/FINK/ Fink/

