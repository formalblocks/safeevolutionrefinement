import sys
import os
import shutil
import re

def copy_input_contract_files(source_path, sim_contracts_path='contracts'):
    # Check if an argument is provided
    if not source_path:
        print("Usage: {} <input_source_folder_path>".format(source_path))
        sys.exit(1)

    files_paths = os.listdir(source_path)
    assert len(files_paths) == 2, 'There must be only two files representing two version of the same contract'

    # Check if source folder exists
    if not os.path.isdir(source_path):
        print("Source folder does not exist")
        sys.exit(1)
    
    filename = os.path.basename(source_path)
    source_path = source_path.rstrip('/')
    
    # Check if destination files exist
    if not (os.path.exists(os.path.join(source_path, f"{filename}1.sol")) or os.path.exists(os.path.join(source_path, f"{filename}2.sol"))):
        print(f"File {source_path}/{filename}1.sol or {source_path}/{filename}2.sol do not exist")
        sys.exit(1)
    
    
    # Check if simulation folder exists
    if not os.path.isdir(sim_contracts_path):
        print(f"{sim_contracts_path} folder does not exist")
        sys.exit(1)
    
    # Clear simulation folder
    for file in os.listdir(sim_contracts_path):
        file_path = os.path.join(sim_contracts_path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    
    # Copy files from source folder to destination folder
    for item in os.listdir(source_path):
        item_path = os.path.join(source_path, item)
        if os.path.isfile(item_path):
            shutil.copy(item_path, sim_contracts_path)
    
    print(f"Files copied successfully from {source_path} to {sim_contracts_path}")
    return files_paths

def _inject_aux(code):
    pattern = r'(^\s*?contract.*?{)([\s\S]+)'

    # Substituindo o padrão com os emit events
    code_with_aux_emit = re.sub(pattern, 
    r"""\1

    function emitMap(string memory fun, address keyaddr) public {
        emit Map(fun, keyaddr, 0, 0x0);
    }

    function emitMap(string memory fun, uint keyint) public {
        emit Map(fun, address(0), keyint, 0x0);
    }

    function emitMap(string memory fun, bytes4 keybytes) public {
        emit Map(fun, address(0), 0, keybytes);
    }


    event Map(string fun, address keyaddr, uint keyint, bytes4 keybytes);
\2
""", code, flags=re.MULTILINE)

    return code_with_aux_emit

def inject_emit_map(contracts_dir):
    files_paths = os.listdir(contracts_dir)
    for file in files_paths:
        filepath = os.path.join(contracts_dir, file)
        if os.path.isfile(filepath):
            f = open(filepath, 'r+')
            content = f.read()
            if not 'event Map' in content:
                content = _inject_aux(content)
                # File is not yet annotated
                pattern = r'^(\s*?)(\b\w+\b)\[(.*?)\](.*$)'
                code_with_emit = re.sub(pattern, r'\1\2[\3]\4\n\1emitMap("\2", \3);', content, flags=re.MULTILINE)
                f.seek(0)
                f.write(code_with_emit)
                f.flush()
            
            os.fsync(f)
            f.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: {} <contracts_folder>".format(sys.argv[0]))
        sys.exit(1)

    contracts_folder = sys.argv[1]
    inject_emit_map(contracts_folder)