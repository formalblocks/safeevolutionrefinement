// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity >= 0.5.0;

import "./interfaces/IFYDai.sol";
import "./interfaces/YieldFlashBorrowerLike.sol";
import { IERC3156FlashBorrower, IERC3156FlashLender } from "../interfaces/IERC3156.sol";


/**
 * YieldFYDaiLender allows flash loans of fyDai compliant with ERC-3156: https://github.com/ethereum/EIPs/blob/master/EIPS/eip-3156.md
 */
contract YieldFYDaiERC3156 is IERC3156FlashLender, YieldFlashBorrowerLike {

    /// @dev Fee charged on top of a fyDai flash loan.
    function flashFee(address, uint256) public view  returns (uint256) {
        return 0;
    }

    /// @dev Maximum fyDai flash loan available.
    function flashSupply(address fyDai) public view  returns (uint256) {
        return type(uint112).max - IFYDai(fyDai).totalSupply(); // Can't overflow
    }

    /// @dev ERC-3156 entry point to send `fyDaiAmount` fyDai to `receiver` as a flash loan.
    function flashLoan(address receiver, address fyDai, uint256 fyDaiAmount, bytes memory data) public  {
        bytes memory wrappedData = abi.encode(data, msg.sender, receiver);
        IFYDai(fyDai).flashMint(fyDaiAmount, wrappedData);
    }

    /// @dev FYDai `flashMint` callback, which bridges to the ERC-3156 `onFlashLoan` callback.
    function executeOnFlashMint(uint256 fyDaiAmount, bytes memory wrappedData) public  {
        (bytes memory data, address sender, address receiver) = abi.decode(wrappedData, (bytes, address, address));
        IERC3156FlashBorrower(receiver).onFlashLoan(sender, msg.sender, fyDaiAmount, 0, data); // msg.sender is the lending fyDai contract
    }
}
