pragma solidity ^0.5.0;

contract Paper2 {

    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);


    constructor() public {
        users[address(1)].balance = 2;
        users[address(2)].balance = 2;
    }

    function transfer(address _to, uint256 _value) public returns (bool success) {
        //Default assumes totalSupply can't be over max (2^256 - 1).
        //If your token leaves out totalSupply and can issue more tokens as time goes on, you need to check if it doesn't wrap.
        //Replace the if with this one instead.
        require(users[msg.sender] .balance>= _value && users[_to].balance + _value > users[_to].balance);
        require(users[msg.sender] .balance>= _value);
        users[msg.sender] .balance-= _value;
        users[_to].balance += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }


    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        //same as above. Replace this line with the following if you want to protect against wrapping uints.
        require(users[_from].balance >= _value && allowed[_from][msg.sender] >= _value && users[_to].balance + _value > users[_to].balance);
        require(users[_from].balance >= _value && allowed[_from][msg.sender] >= _value);
        users[_to].balance += _value;
        users[_from].balance -= _value;
        allowed[_from][msg.sender] -= _value;
        emit Transfer(_from, _to, _value);
        return true;
    }


    function balanceOf(address _owner) public returns (uint256 balance) {
        return users[_owner].balance;
    }


    function approve(address _spender, uint256 _value) public returns (bool success) {
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }


    function allowance(address _owner, address _spender) public returns (uint256 remaining) {
      return allowed[_owner][_spender];
    }

    struct User {
        uint256 balance;
    }

    mapping (address => User) public users;
    mapping (address => mapping (address => uint256)) allowed;
}