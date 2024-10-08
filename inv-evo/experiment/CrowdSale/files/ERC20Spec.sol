pragma solidity >=0.5.0;


contract ERC20Spec {

    mapping(address=>uint) internal balances ;
    mapping (address => mapping (address => uint)) internal allowances ;

    mapping(address=>bool) internal  minters ;  // specific for Mintable-ERC20
    mapping(address=>bool) internal  burners ;  // specific for Burnable-ERC20

    constructor () public {
        balances[address(1)] = 2;
        balances[address(2)] = 2;
    }

   function balance(address account) public view returns (uint) {
	    return balances[account];
   }


   function allowance(address owner, address beneficiary) public view returns (uint) {
	    return allowances[owner][beneficiary];
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
        @notice postcondition allowances[msg.sender][to] == val
        @notice modifies allowances[msg.sender] */

    function approve(address to, uint val) public {
	    allowances[msg.sender][to] = val;
    }



   /**  @notice precondition to != address(0)
	    @notice precondition to != from
        @notice precondition allowances[from][msg.sender] - val >= 0
	    @notice precondition  balances[to] + val >= balances[to]
	    @notice precondition  balances[from] - val >= 0
        @notice postcondition balances[to] == __verifier_old_uint(balances[to]) + val
	    @notice postcondition balances[from] == __verifier_old_uint(balances[from]) - val
        @notice postcondition allowances[from][msg.sender] == __verifier_old_uint(allowances[from][msg.sender]) - val
        @notice modifies balances[to]
        @notice modifies balances[from]
        @notice modifies allowances[from] */

    function transferFrom(address from, address to, uint val) public {
	    balances[from] = balances[from] - val;
	    balances[to] = balances[to] + val;
	    allowances[from][msg.sender] = allowances[from][msg.sender] - val;
    }



   /**  @notice precondition spender != address(0)
        @notice precondition allowances[msg.sender][spender] + val >= allowances[msg.sender][spender]
        @notice postcondition allowances[msg.sender][spender] == __verifier_old_uint(allowances[msg.sender][spender]) + val
        @notice modifies allowances[msg.sender] */

    function increaseAllowance(address spender, uint val) public {
	    allowances[msg.sender][spender] = allowances[msg.sender][spender] + val;
    }



   /**  @notice precondition spender != address(0)
        @notice precondition allowances[msg.sender][spender] - val >= 0
        @notice postcondition allowances[msg.sender][spender] == __verifier_old_uint(allowances[msg.sender][spender]) - val
        @notice modifies allowances[msg.sender] */

    function decreaseAllowance(address spender, uint val) public {
	    allowances[msg.sender][spender] = allowances[msg.sender][spender] - val;
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