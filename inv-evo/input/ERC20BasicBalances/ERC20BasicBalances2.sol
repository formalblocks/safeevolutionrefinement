pragma solidity ^0.5.0;

contract ERC20BasicBalances2 {

    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);


    constructor() public {
        balances_[address(1)] = 2;
        balances_[address(2)] = 2;
    }

    /// @notice  postcondition ( ( balances_[msg.sender] ==  __verifier_old_uint (balances_[msg.sender] ) - _value  && msg.sender  != _to ) ||   ( balances_[msg.sender] ==  __verifier_old_uint ( balances_[msg.sender]) && msg.sender  == _to ) &&  success )   || !success
    /// @notice  postcondition ( ( balances_[_to] ==  __verifier_old_uint ( balances_[_to] ) + _value  && msg.sender  != _to ) ||   ( balances_[_to] ==  __verifier_old_uint ( balances_[_to] ) && msg.sender  == _to ) &&  success )   || !success
    /// @notice  emits  Transfer 
    function transfer(address _to, uint256 _value) public returns (bool success) {
        //Default assumes totalSupply can't be over max (2^256 - 1).
        //If your token leaves out totalSupply and can issue more tokens as time goes on, you need to check if it doesn't wrap.
        //Replace the if with this one instead.
        require(balances_[msg.sender] >= _value && balances_[_to] + _value > balances_[_to]);
        require(balances_[msg.sender] >= _value);
        balances_[msg.sender] -= _value;
        balances_[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    /// @notice  postcondition ( ( balances_[_from] ==  __verifier_old_uint (balances_[_from] ) - _value  &&  _from  != _to ) ||   ( balances_[_from] ==  __verifier_old_uint ( balances_[_from] ) &&  _from== _to ) &&  success )   || !success
    /// @notice  postcondition ( ( balances_[_to] ==  __verifier_old_uint ( balances_[_to] ) + _value  &&  _from  != _to ) ||   ( balances_[_to] ==  __verifier_old_uint ( balances_[_to] ) &&  _from  ==_to ) &&  success )   || !success
    /// @notice  postcondition  (allowed[_from ][msg.sender] ==  __verifier_old_uint (allowed[_from ][msg.sender] ) - _value && success)  || (allowed[_from ][msg.sender] ==  __verifier_old_uint (allowed[_from ][msg.sender] ) && !success) || _from  == msg.sender
    /// @notice  postcondition  allowed[_from ][msg.sender]  <= __verifier_old_uint (allowed[_from ][msg.sender] ) ||  _from  == msg.sender
    /// @notice  emits  Transfer
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        //same as above. Replace this line with the following if you want to protect against wrapping uints.
        require(balances_[_from] >= _value && allowed[_from][msg.sender] >= _value && balances_[_to] + _value > balances_[_to]);
        require(balances_[_from] >= _value && allowed[_from][msg.sender] >= _value);
        balances_[_to] += _value;
        balances_[_from] -= _value;
        allowed[_from][msg.sender] -= _value;
        emit Transfer(_from, _to, _value);
        return true;
    }

    /// @notice postcondition balances_[_owner] == balance
    function balanceOf(address _owner) public returns (uint256 balance) {
        return balances_[_owner];
    }

    /// @notice  postcondition (allowed[msg.sender ][ _spender] ==  _value  &&  success) || ( allowed[msg.sender ][ _spender] ==  __verifier_old_uint ( allowed[msg.sender ][ _spender] ) && !success )    
    /// @notice  emits  Approval
    function approve(address _spender, uint256 _value) public returns (bool success) {
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    /// @notice postcondition allowed[_owner][_spender] == remaining
    function allowance(address _owner, address _spender) public returns (uint256 remaining) {
      return allowed[_owner][_spender];
    }

    mapping (address => uint256) public balances_;
    mapping (address => mapping (address => uint256)) allowed;
}