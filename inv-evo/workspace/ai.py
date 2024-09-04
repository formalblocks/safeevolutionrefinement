from openai import OpenAI

client = OpenAI(api_key='')

def infer_abstraction_function(file1_content, file2_content):

    prompt = f'''Given the Solidity files:
                File 1:{file1_content}
                File 2:{file2_content}
                Please infer an equation between the changed and new variables from the first contract 
                to the second. Return only the equation/expression. Do not explain. 
                Desconsider the constructor. Do not rename the variables.
                Only one response per new/changed variable. Do not show variables that are equal.
                Use quantifiers in mappings similiar to solc-verify
                '''

    # Call the OpenAI API
    response = client.chat.completions.create(model="gpt-4-1106-preview",
        messages = [{'role': 'user', 'content': prompt}],
        temperature=0.1)

    # Return the response
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    # Example Solidity files
    file1_content = """
    contract Token {

        address public owner;
        address public config;
        bool public locked;
        address public dao;
        address public badgeLedger;
        uint256 public totalSupply;

        mapping (address => uint256) balances;
        mapping (address => mapping (address => uint256)) allowed;
        mapping (address => bool) seller;

        

        modifier ifSales() {
            if (!seller[msg.sender]) revert(); 
            _;
        }

        modifier ifOwner() {
            if (msg.sender != owner) revert();
            _;
        }

        modifier ifDao() {
            if (msg.sender != dao) revert();
            _;
        }

        event Transfer(address indexed _from, address indexed _to, uint256 _value);
        event Mint(address indexed _recipient, uint256 indexed _amount);
        event Approval(address indexed _owner, address indexed _spender, uint256  _value);

        constructor(address _config) public {
            config = _config;
            owner = msg.sender;
            // address _initseller = ConfigInterface(_config).getConfigAddress("sale1:address");
            // seller[_initseller] = true; 
            // badgeLedger = new Badge(_config);
            locked = false;
        }

        function safeToAdd(uint a, uint b) public returns (bool) {
            return (a + b >= a);
        }

        function addSafely(uint a, uint b) public returns (uint result) {
            if (!safeToAdd(a, b)) {
            revert();
            } else {
            result = a + b;
            return result;
            }
        }

        function safeToSubtract(uint a, uint b) public returns (bool) {
            return (b <= a);
        }

        function subtractSafely(uint a, uint b) public returns (uint) {
            if (!safeToSubtract(a, b)) revert();
            return a - b;
        }

        function balanceOf(address _owner) public returns (uint256 balance) {
            return balances[_owner];
        }

        function transfer(address _to, uint256 _value) public returns (bool success) {
            if (balances[msg.sender] >= _value && _value > 0) {
            balances[msg.sender] -= _value;
            balances[_to] += _value;
            emit Transfer(msg.sender, _to, _value);
            success = true;
            } else {
            success = false;
            }
            return success;
        }

        function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
            if (balances[_from] >= _value && allowed[_from][msg.sender] >= _value && _value > 0) {
            balances[_to] += _value;
            balances[_from] -= _value;
            allowed[_from][msg.sender] -= _value;
            emit Transfer(_from, _to, _value);
            return true;
            } else {
            return false;
            }
        }

        function approve(address _spender, uint256 _value) public returns (bool success) {
            allowed[msg.sender][_spender] = _value;
            emit Approval(msg.sender, _spender, _value);
            success = true;
            return success;
        }

        function allowance(address _owner, address _spender) public returns (uint256 remaining) {
            remaining = allowed[_owner][_spender];
            return remaining;
        }
        function mint(address _owner, uint256 _amount) public ifSales returns (bool success) {
            totalSupply = addSafely(_amount, totalSupply);
            balances[_owner] = addSafely(balances[_owner], _amount);
            return true;
        }

        function mintBadge(address _owner, uint256 _amount) public ifSales returns (bool success) {
            if (!Badge(badgeLedger).mint(_owner, _amount)) return false;
            return true;
        }

        function registerDao(address _dao) public ifOwner returns (bool success) {
            if (locked == true) return false;
            dao = _dao;
            locked = true;
            return true;
        }

        function registerSeller(address _tokensales) public ifDao returns (bool success) {
            seller[_tokensales] = true;
            return true;
        }

        function unregisterSeller(address _tokensales) public ifDao returns (bool success) {
            seller[_tokensales] = false;
            return true;
        }

        function setOwner(address _newowner) public ifDao returns (bool success) {
            if(Badge(badgeLedger).setOwner(_newowner)) {
            owner = _newowner;
            success = true;
            } else {
            success = false;
            }
            return success;
        }

        function setDao(address _newdao) public ifDao returns (bool success) {
            dao = _newdao;
        }
        }
    """

    file2_content = """
    contract TokenInterface {

        struct User {
            bool locked;
            uint256 balance;
            uint256 badges;
            mapping (address => uint256) allowed;
        }

        mapping (address => User) users;
        mapping (address => uint256) balances;
        mapping (address => mapping (address => uint256)) allowed;
        mapping (address => bool) seller;

        address config;
        address owner;

        /// @return total amount of tokens
        uint256 public totalSupply;
        uint256 public totalBadges;

        /// @param _owner The address from which the balance will be retrieved
        /// @return The balance
        function balanceOf(address _owner) public returns (uint256 balance);

        /// @param _owner The address from which the badge count will be retrieved
        /// @return The badges count
        function badgesOf(address _owner) public returns (uint256 badge);

        /// @notice send `_value` tokens to `_to` from `msg.sender`
        /// @param _to The address of the recipient
        /// @param _value The amount of tokens to be transfered
        /// @return Whether the transfer was successful or not
        function transfer(address _to, uint256 _value) public returns (bool success);

        /// @notice send `_value` badges to `_to` from `msg.sender`
        /// @param _to The address of the recipient
        /// @param _value The amount of tokens to be transfered
        /// @return Whether the transfer was successful or not
        function sendBadge(address _to, uint256 _value) public returns (bool success);

        /// @notice send `_value` tokens to `_to` from `_from` on the condition it is approved by `_from`
        /// @param _from The address of the sender
        /// @param _to The address of the recipient
        /// @param _value The amount of tokens to be transfered
        /// @return Whether the transfer was successful or not
        function transferFrom(address _from, address _to, uint256 _value) public returns (bool success);

        /// @notice `msg.sender` approves `_spender` to spend `_value` tokens on its behalf
        /// @param _spender The address of the account able to transfer the tokens
        /// @param _value The amount of tokens to be approved for transfer
        /// @return Whether the approval was successful or not
        function approve(address _spender, uint256 _value) public returns (bool success);

        /// @param _owner The address of the account owning tokens
        /// @param _spender The address of the account able to transfer the tokens
        /// @return Amount of remaining tokens of _owner that _spender is allowed to spend
        function allowance(address _owner, address _spender) public returns (uint256 remaining);

        /// @notice mint `_amount` of tokens to `_owner`
        /// @param _owner The address of the account receiving the tokens
        /// @param _amount The amount of tokens to mint
        /// @return Whether or not minting was successful
        function mint(address _owner, uint256 _amount) public returns (bool success);

        /// @notice mintBadge Mint `_amount` badges to `_owner`
        /// @param _owner The address of the account receiving the tokens
        /// @param _amount The amount of tokens to mint
        /// @return Whether or not minting was successful
        function mintBadge(address _owner, uint256 _amount) public returns (bool success);

        
        event SendBadge(address indexed _from, address indexed _to, uint256 _amount);
        
        }
    """

    inferred_abstract_function = infer_abstraction_function(file1_content, file2_content)

    print("Inferred Abstraction Function:")
    print(inferred_abstract_function)