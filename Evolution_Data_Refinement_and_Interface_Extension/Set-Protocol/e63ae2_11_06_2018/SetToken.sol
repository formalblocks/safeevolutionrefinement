/*
    Copyright 2018 Set Labs Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
*/

pragma solidity >=0.5.0 <0.9.0;
pragma experimental "ABIEncoderV2";


import { DetailedERC20 } from "./DetailedERC20.sol";
import { ERC20 } from "./ERC20.sol";
import { StandardToken } from "./StandardToken.sol";
import { SafeMath } from "./SafeMath.sol";
import "./AddressArrayUtils.sol";


/**
 * @title {Set}
 * @author Felix Feng
 *
 * @dev Implementation of the basic {Set} token.
 *
 */
contract SetToken is
    StandardToken,
    DetailedERC20
{
    using SafeMath for uint256;
    using AddressArrayUtils for address[];

    /* ============ Constants ============ */
    
    string constant COMPONENTS_INPUT_MISMATCH = "Components and units must be the same length.";
    string constant COMPONENTS_MISSING = "Components must not be empty.";
    string constant UNITS_MISSING = "Units must not be empty.";
    string constant ZERO_QUANTITY = "Quantity must be greater than zero.";

    /* ============ Structs ============ */

    struct Component {
        address address_;
        uint unit_;
    }

    /* ============ State Variables ============ */

    uint public naturalUnit;
    Component[] public components;

    // Mapping of componentHash to isComponent
    mapping(bytes32 => bool) internal isComponent;

    /* ============ Modifiers ============ */

    modifier isMultipleOfNaturalUnit(uint _quantity) {
        require((_quantity % naturalUnit) == 0);
        _;
    }

    // Confirm that all inputs for creating a set are valid
    modifier areValidCreationParameters(address[] memory _components, uint[] memory _units) {
        // Confirm an empty _components array is not passed
        require(
            _components.length > 0,
            COMPONENTS_MISSING
        );

        // Confirm an empty _quantities array is not passed
        require(
            _units.length > 0,
            UNITS_MISSING
        );

        // Confirm there is one quantity for every token address
        require(
            _components.length == _units.length,
            COMPONENTS_INPUT_MISMATCH
        );
        _;
    }

    modifier isNonZero(uint _quantity) {
        require(
            _quantity > 0,
            ZERO_QUANTITY
        );
        _;
    }


    modifier validDestination(address _to) {
        require(_to != address(0));
        require(_to != address(this));
        _;
    }


    /* ============ Public Functions ============ */

    function mint(
        uint quantity
    )
        external
    {
        balances[msg.sender] = balances[msg.sender].add(quantity);
        totalSupply_ = totalSupply_.add(quantity);
        emit Transfer(address(0), msg.sender, quantity);
    }

    function burn(
        uint quantity
    )
        external
    {
        balances[msg.sender] = balances[msg.sender].sub(quantity);
        totalSupply_ = totalSupply_.sub(quantity);
        emit Transfer(msg.sender, address(0), quantity);
    }

    // /* ============ Getters ============ */

    function getComponents()
        public
        view
        returns(address[] memory)
    {
        address[] memory componentAddresses = new address[](components.length);
        for (uint16 i = 0; i < components.length; i++) {
            componentAddresses[i] = components[i].address_;
        }
        return componentAddresses;
    }

    function getUnits()
        public
        view
        returns(uint[] memory)
    {
        uint[] memory units = new uint[](components.length);
        for (uint16 i = 0; i < components.length; i++) {
            units[i] = components[i].unit_;
        }
        return units;
    }

    // /* ============ Transfer s ============ */

    function transfer(
        address _to,
        uint256 _value
    )
        public
        validDestination(_to)
        returns (bool)
    {
        return super.transfer(_to, _value);
    }

    function transferFrom(
        address _from,
        address _to,
        uint256 _value
    )
        public
        validDestination(_to)
        returns (bool)
    {
        return super.transferFrom(_from, _to, _value);
    }

    /* ============ Private Helpers ============ */

    function tokenIsComponent(
        address _tokenAddress
    )
        view
        internal
        returns (bool)
    {
        // return isComponent[keccak256(_tokenAddress)];
    }

}
