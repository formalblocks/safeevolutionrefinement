import re

def inject_emit_events(code):
    # Definindo o padrão de busca
    pattern = r'^(\s*?)(\b\w+\b)\[(.*?)\](.*$)'

    # Substituindo o padrão com os emit events
    code_with_emit = re.sub(pattern, r'\1\2[\3]\4\n\1emitmap("\2", \3);', code, flags=re.MULTILINE)

    return code_with_emit

def inject_aux(code):
    pattern = r'(^\s*?contract.*?{)([\s\S]+)'

    # Substituindo o padrão com os emit events
    code_with_emit = re.sub(pattern, 
    r"""\1
event Map(string fun, address keyaddr, uint keyint);

function __emitmap(string fun, address keyaddr) public {
    emit Map(fun, keyaddr, 0);
}

function __emitmap(string fun, uint keyint) {
    emit Map(fun, 0x0, keyint);
}
\2
""", code, flags=re.MULTILINE)

    return code_with_emit
    

# Exemplo de código para teste
code = '''

contract Hello{
function transfer(address receiver, uint numTokens) public returns (bool) {
    require(numTokens <= balances_[msg.sender]);
    
    balances_[msg.sender] = balances_[msg.sender].sub(numTokens - 1);
    balances_[receiver] = balances_[receiver].add(numTokens + 1);
    emit Transfer(msg.sender, receiver, numTokens);
    return true;
}
}
'''

modified_code = inject_aux(code)
print(modified_code)