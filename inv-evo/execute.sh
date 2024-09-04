#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <input_source_folder_path>"
    exit 1
fi

# Check if source folder exists
if [ ! -d "$1" ]; then
    echo "Source folder does not exist"
    exit 1
fi
source_path_leading=$1
source_path=${source_path_leading%/}
filename=$(basename "$source_path")

# Check if destination folder exists, if not create it
if [ ! -e "$source_path/${filename}1.sol" ] || [ ! -e "$source_path/${filename}2.sol" ]; then
    echo "File $source_path/${filename}1.sol or $source_path/${filename}2.sol do not exist"
    exit 1
fi

sim_contracts_path="simulation/contracts"

# Check if source folder exists
if [ ! -d "$sim_contracts_path" ]; then
    echo "$sim_contracts_path folder does not exist"
    exit 1
fi

rm -r $PWD/$sim_contracts_path/*

# Copy two files from source folder to destination folder
cp -r $PWD/$source_path/* $sim_contracts_path

echo "Files copied successfully from $source_path to $sim_contracts_path"

python preprocess.py $sim_contracts_path

echo "Injected events in the contract source code to track mapping updates during transactions"

cd simulation
brownie run simulate.py
