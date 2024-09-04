/**
 * @notice invariant accs[address(this)].bal == 0
 * @notice invariant forall (address addr) accs[addr].bal == 0 || accs[addr].is_open 
 */
contract ToyWallet {


	struct Account {
		uint bal;
		bool is_open;
	}

	mapping (address => Account) accs;
	address[] used_accs;
	mapping (address => bool) used;

	/**
	* @notice postcondition forall (address addr) accs[addr].bal == 0
	*/
	constructor() public {
		require(false);
	}

	/**
	* @notice postcondition __verifier_old_address(msg.sender) != __verifier_old_address(address(this))
	* @notice postcondition address(this).balance == __verifier_old_uint(address(this).balance) + msg.value
	* @notice postcondition accs[msg.sender].bal == __verifier_old_uint(accs[msg.sender].bal) + msg.value
	* @notice postcondition forall (address addr) addr == msg.sender || __verifier_old_uint(accs[addr].bal) == accs[addr].bal
	*/
	function deposit () payable public {
		require(msg.sender != address(this));
		require(accs[msg.sender].is_open);
		accs[msg.sender].bal = accs[msg.sender].bal + msg.value;
		if (!used[msg.sender]){
			used[msg.sender] = true;
			used_accs.push(msg.sender);
		}
	}

	/**
	* @notice postcondition __verifier_old_uint(accs[msg.sender].bal) >= __verifier_old_uint(value)
	* @notice postcondition __verifier_old_address(msg.sender) != __verifier_old_address(address(this))
	* @notice postcondition address(this).balance == __verifier_old_uint(address(this).balance) - value
	* @notice postcondition accs[msg.sender].bal == __verifier_old_uint(accs[msg.sender].bal) - value
	* @notice postcondition forall (address addr) addr == msg.sender || __verifier_old_uint(accs[addr].bal) == accs[addr].bal
	*/
	function withdraw (uint value) public {
		require(accs[msg.sender].bal >= value);
		require(msg.sender != address(this));
		require(accs[msg.sender].is_open);
		bool ok;
		// Buggy
		// (ok,) = msg.sender.call.value(value)("");
		// Correct
		ok = msg.sender.send(value);
		if (!ok){
			revert();
		}
		accs[msg.sender].bal = accs[msg.sender].bal - value;
	}

	/**
	* @notice postcondition accs[msg.sender].is_open
	*/
	function open() public {
		require(!accs[msg.sender].is_open);
		require(accs[msg.sender].bal == 0);
		accs[msg.sender].is_open = true;
	}

	// /**
	// * @notice postcondition !is_open[msg.sender]
	// */
	// function close() public {
	// 	require(is_open[msg.sender]);
	// 	require(accs[msg.sender] == 0);
	// 	is_open[msg.sender] = false;
	// }
}	