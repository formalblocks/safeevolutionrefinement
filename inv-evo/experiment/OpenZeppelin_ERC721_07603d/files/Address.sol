pragma solidity >=0.5.0 <0.9.0;

/**
 * Utility library of inline functions on addresses
 */
library Address {
    
    function isContract(address account) internal view returns (bool) {
        // uint256 size;
        // // XXX Currently there is no better way to check if there is a contract in an address
        // // than to check the size of the code at that address.
        // // See https://ethereum.stackexchange.com/a/14016/36603
        // // for more details about how this works.
        // // TODO Check this again before the Serenity release, because all addresses will be
        // // contracts then.
        // // solhint-disable-next-line no-inline-assembly
        // assembly { size := extcodesize(account) }
        // return size > 0;
    }
}