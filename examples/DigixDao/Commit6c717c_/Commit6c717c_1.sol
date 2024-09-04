pragma solidity ^0.5.0;

contract Commit6c717c_1 {

    struct User {
        // bool locked;
        uint256 balance;
        // uint256 badges;
        mapping (address => uint256) allowed;
    }

  mapping (address => User) public users;

  modifier noEther() {
    if (msg.value > 0) revert();
    _;
  }

      constructor () public {
        users[address(1)].balance = 2;
        users[address(1)].allowed[address(2)] = 2;
        users[address(2)].balance = 2;
        users[address(2)].allowed[address(1)] = 2;
    }

//   constructor (address _config) public {
//     config = _config;
//     owner = msg.sender;
//     // address _initseller = ConfigInterface(_config).getConfigAddress("sale1:address");
//     // seller[_initseller] = true; 
//     // badgeLedger = new Badge(_config);
//     locked = false;
//   }

  /// @notice postcondition  users[_owner].balance == balance
  function balanceOf(address _owner) public returns (uint256 balance) {
    return users[_owner].balance;
  }

  /// @notice  postcondition ( ( users[msg.sender].balance ==  __verifier_old_uint (users[msg.sender].balance ) - _value  && msg.sender  != _to ) ||   ( users[msg.sender].balance ==  __verifier_old_uint ( users[msg.sender].balance ) && msg.sender  == _to ) &&  success )  || !success
  /// @notice  postcondition ( ( users[_to].balance ==  __verifier_old_uint ( users[_to].balance ) + _value  && msg.sender  != _to ) ||   ( users[_to].balance ==  __verifier_old_uint ( users[_to].balance ) && msg.sender  == _to ) &&  success )   || !success
  /// @notice  emits  Transfer 
  function transfer(address _to, uint256 _value) public returns (bool success) {
    if (users[msg.sender].balance >= _value && _value > 0) {
      users[msg.sender].balance -= _value;
      users[_to].balance += _value;
      emit Transfer(msg.sender, _to, _value);
      success = true;
    } else {
      success = false;
    }
    return success;
  }

  /// @notice  postcondition ( ( users[_from].balance ==  __verifier_old_uint (users[_from].balance ) - _value  &&  _from  != _to ) || ( users[_from].balance ==  __verifier_old_uint ( users[_from].balance ) &&  _from == _to ) &&  success ) || !success
  /// @notice  postcondition ( ( users[_to].balance ==  __verifier_old_uint ( users[_to].balance ) + _value  &&  _from  != _to ) || ( users[_to].balance ==  __verifier_old_uint ( users[_to].balance ) &&  _from  == _to ) &&  success ) || !success
  /// @notice  postcondition ( users[_from ].allowed[msg.sender] ==  __verifier_old_uint (users[_from ].allowed[msg.sender] ) - _value ) || ( users[_from ].allowed[msg.sender] ==  __verifier_old_uint (users[_from ].allowed[msg.sender] ) && !success) ||  _from  == msg.sender
  /// @notice  postcondition  users[_from ].allowed[msg.sender]  <= __verifier_old_uint (users[_from ].allowed[msg.sender] ) ||  _from  == msg.sender
  /// @notice  emits  Transfer
  function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
    if (users[_from].balance >= _value && users[_from].allowed[msg.sender] >= _value && _value > 0) {
      users[_to].balance += _value;
      users[_from].balance -= _value;
      users[_from].allowed[msg.sender] -= _value;
      emit Transfer(_from, _to, _value);
      return true;
    } else {
      return false;
    }
  }

  /// @notice  postcondition (users[msg.sender ].allowed[ _spender] ==  _value  &&  success) || ( users[msg.sender ].allowed[ _spender] ==  __verifier_old_uint ( users[msg.sender ].allowed[ _spender] ) && !success )    
  /// @notice  emits  Approval
  function approve(address _spender, uint256 _value) public returns (bool success) {
    users[msg.sender].allowed[_spender] = _value;
    emit Approval(msg.sender, _spender, _value);
    return true;
  }

  /// @notice postcondition users[_owner].allowed[_spender] == remaining
  function allowance(address _owner, address _spender) public returns (uint256 remaining) {
    return users[_owner].allowed[_spender];
  }

//   function mint(address _owner, uint256 _amount) public ifSales returns (bool success) {
//     totalSupply += _amount;
//     users[_owner].balance += _amount;
//     return true;
//   }

//   function mintBadge(address _owner, uint256 _amount) public ifSales returns (bool success) {
//     if (!Badge(badgeLedger).mint(_owner, _amount)) return false;
//     return true;
//   }

//   function registerDao(address _dao) public ifOwner returns (bool success) {
//     if (locked == true) return false;
//     dao = _dao;
//     locked = true;
//     return true;
//   }

//   function registerSeller(address _tokensales) public ifDao returns (bool success) {
//     seller[_tokensales] = true;
//     return true;
//   }

  event Transfer(address indexed _from, address indexed _to, uint256 _value);
  event Approval(address indexed _owner, address indexed _spender, uint256 _value);
}