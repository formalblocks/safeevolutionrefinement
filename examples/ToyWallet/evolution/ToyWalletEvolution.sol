/**
 * @notice invariant accs[address(this)] == 0
 */
contract ToyWallet {
	mapping (address => uint) accs;
	address[] used_accs;
	mapping (address => bool) used;

	/**
	* @notice postcondition forall (address addr) accs[addr] == 0
	*/
	constructor() public {
	}

	/**
	* @notice postcondition __verifier_old_address(msg.sender) != __verifier_old_address(address(this))
	* @notice postcondition address(this).balance == __verifier_old_uint(address(this).balance) + msg.value
	* @notice postcondition accs[msg.sender] == __verifier_old_uint(accs[msg.sender]) + msg.value
	* @notice postcondition forall (address addr) addr == msg.sender || __verifier_old_uint(accs[addr]) == accs[addr]
	*/
	function deposit () payable public {
		require(msg.sender != address(this));
		accs[msg.sender] = accs[msg.sender] + msg.value;
		if (!used[msg.sender]){
			used[msg.sender] = true;
			used_accs.push(msg.sender);
		}
	}

	/**
	* @notice postcondition __verifier_old_uint(accs[msg.sender]) >= __verifier_old_uint(value)
	* @notice postcondition __verifier_old_address(msg.sender) != __verifier_old_address(address(this))
	* @notice postcondition address(this).balance == __verifier_old_uint(address(this).balance) - value
	* @notice postcondition accs[msg.sender] == __verifier_old_uint(accs[msg.sender]) - value
	* @notice postcondition forall (address addr) addr == msg.sender || __verifier_old_uint(accs[addr]) == accs[addr]
	*/
	function withdraw (uint value) public {
		require(accs[msg.sender] >= value);
		require(msg.sender != address(this));
		bool ok;
		// Buggy
		// (ok,) = msg.sender.call.value(value)("");
		// Correct
		ok = msg.sender.send(value);
		if (!ok){
			revert();
		}
		accs[msg.sender] = accs[msg.sender] - value;
	}
}	