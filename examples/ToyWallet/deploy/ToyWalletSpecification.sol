// SPDX-License-Identifier: MIT
pragma solidity >= 0.5.0;

/**
 * @notice invariant accs[address(this)] == 0
 */
contract ToyWallet {
	mapping (address => uint) accs;

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
	}

	/**
	* @notice postcondition __verifier_old_uint(accs[msg.sender]) >= __verifier_old_uint(value)
	* @notice postcondition __verifier_old_address(msg.sender) != __verifier_old_address(address(this))
	* @notice postcondition address(this).balance == __verifier_old_uint(address(this).balance) - value
	* @notice postcondition accs[msg.sender] == __verifier_old_uint(accs[msg.sender]) - value
	* @notice postcondition forall (address addr) addr == msg.sender || __verifier_old_uint(accs[addr]) == accs[addr]
	*/
	function withdraw (uint value) public {
	}
}	