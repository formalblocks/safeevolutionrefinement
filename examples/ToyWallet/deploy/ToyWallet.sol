// SPDX-License-Identifier: MIT
pragma solidity >= 0.5.0;

contract ToyWallet {
	mapping (address => uint) accs;

	constructor() public {
	}

	function deposit () payable public {
		require(msg.sender != address(this));
		accs[msg.sender] = accs[msg.sender] + msg.value;
	}

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