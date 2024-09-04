pragma solidity >=0.5.0;


contract ERC20 {

    mapping(address=>uint) public balances ;
    mapping (address => mapping (address => uint)) public _allowed ; // no support



    constructor () public {
        balances[address(1)] = 2;
        balances[address(2)] = 2;
    }

   function balance(address account) public view returns (uint) {
	    return balances[account];
   }


   function allowance(address owner, address beneficiary) public view returns (uint) {
	    return _allowed[owner][beneficiary];
   }


    /** @notice precondition to != address(0)
	    @notice precondition to != msg.sender
        @notice precondition  balances[to] + val >= balances[to]
	    @notice precondition  balances[msg.sender] - val >= 0
        @notice postcondition balances[to] == __verifier_old_uint(balances[to]) + val
	    @notice postcondition balances[msg.sender] == __verifier_old_uint(balances[msg.sender]) - val
        @notice modifies balances[msg.sender]
        @notice modifies balances[to]*/

    function transfer(address to, uint val) public {
	    balances[msg.sender] = balances[msg.sender] - val;
	    balances[to] = balances[to] + val;

    }


    /** @notice precondition to != address(0)
        @notice postcondition _allowed[msg.sender][to] == val
        @notice modifies _allowed[msg.sender] */

    function approve(address to, uint val) public {
	    _allowed[msg.sender][to] = val;
    }



   /**  @notice precondition to != address(0)
	    @notice precondition to != from
        @notice precondition _allowed[from][msg.sender] - val >= 0
	    @notice precondition  balances[to] + val >= balances[to]
	    @notice precondition  balances[from] - val >= 0
        @notice postcondition balances[to] == __verifier_old_uint(balances[to]) + val
	    @notice postcondition balances[from] == __verifier_old_uint(balances[from]) - val
        @notice postcondition _allowed[from][msg.sender] == __verifier_old_uint(_allowed[from][msg.sender]) - val
        @notice modifies balances[to]
        @notice modifies balances[from]
        @notice modifies _allowed[from] */

    function transferFrom(address from, address to, uint val) public {
	    balances[from] = balances[from] - val;
	    balances[to] = balances[to] + val;
	    _allowed[from][msg.sender] = _allowed[from][msg.sender] - val;
    }



   /**  @notice precondition spender != address(0)
        @notice precondition _allowed[msg.sender][spender] + val >= _allowed[msg.sender][spender]
        @notice postcondition _allowed[msg.sender][spender] == __verifier_old_uint(_allowed[msg.sender][spender]) + val
        @notice modifies _allowed[msg.sender] */

    function increaseAllowance(address spender, uint val) public {
	    _allowed[msg.sender][spender] = _allowed[msg.sender][spender] + val;
    }



   /**  @notice precondition spender != address(0)
        @notice precondition _allowed[msg.sender][spender] - val >= 0
        @notice postcondition _allowed[msg.sender][spender] == __verifier_old_uint(_allowed[msg.sender][spender]) - val
        @notice modifies _allowed[msg.sender] */

    function decreaseAllowance(address spender, uint val) public {
	    _allowed[msg.sender][spender] = _allowed[msg.sender][spender] - val;
    }



   /**  @notice precondition to != address(0)
	    @notice precondition minters[msg.sender]
        @notice precondition balances[to] + val >= balances[to]
        @notice postcondition balances[to] == __verifier_old_uint(balances[to]) + val
        @notice modifies balances[to] */

    function mint(address to, uint val) public {
	    balances[to] = balances[to] + val;
    }



   /**  @notice precondition from != address(0)
	    @notice precondition burners[msg.sender]
        @notice precondition balances[from] - val >= 0
        @notice postcondition balances[from] == __verifier_old_uint(balances[from]) - val
        @notice modifies balances[from] */

    function burn(address from, uint val) public {
	    balances[from] = balances[from] - val;
    }

}