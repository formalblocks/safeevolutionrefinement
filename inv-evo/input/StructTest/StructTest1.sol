pragma solidity ^0.5.0;

contract StructTest1 {

    struct X {
        uint a;
        uint b;
    }

    X public x;

    constructor () public {
    }

    function seta(uint y) public {
        x.a = y;
    }

    function setb(uint y) public {
        x.b = y;
    }

}