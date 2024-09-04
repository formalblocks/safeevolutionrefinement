pragma solidity ^0.5.0;

contract StructTest2 {

    uint public a;
    uint public b;

    constructor () public {
    }

    function seta(uint y) public {
        a = y;
    }

    function setb(uint y) public {
        b = y;
    }

}