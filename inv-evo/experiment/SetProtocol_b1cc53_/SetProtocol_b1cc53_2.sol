pragma solidity ^0.5.0;


// import { ERC20Detailed } from "openzeppelin-solidity/contracts/token/ERC20/ERC20Detailed.sol";
import './files/ERC20Detailed.sol';
import './files/ERC20.sol';
import './files/SafeMath.sol';
import './files/Bytes32.sol';
// import { ERC20 } from "openzeppelin-solidity/contracts/token/ERC20/ERC20.sol";
import './files/ISetFactory.sol';


/**
 * @title SetToken
 * @author Set Protocol
 *
 * Implementation of the basic {Set} token.
 */
contract SetProtocol_b1cc53_2 is
    ERC20,
    ERC20Detailed
{
    using SafeMath for uint256;
    using Bytes32 for bytes32;

    /* ============ Structs ============ */

    struct Component {
        address address_;
        uint256 unit_;
    }

    /* ============ State Variables ============ */

    uint256 public naturalUnit;
    Component[] public components;

    // Mapping of componentHash to isComponent
    mapping(address => bool) internal isComponent;

    // Address of the Factory contract that created the SetToken
    address public factory;

    /* ============ Constructor ============ */


    /* ============ Public Functions ============ */

    /*
     * Mint set token for given address.
     * Can only be called by authorized contracts.
     *
     * @param  _issuer      The address of the issuing account
     * @param  _quantity    The number of sets to attribute to issuer
     */
    function mint(
        address _issuer,
        uint256 _quantity
    )
        external
    {
        // Check that function caller is Core
        require(
            msg.sender == ISetFactory(factory).core(),
            "SetToken.mint: Sender must be core"
        );

        _mint(_issuer, _quantity);
    }

    /*
     * Burn set token for given address.
     * Can only be called by authorized contracts.
     *
     * @param  _from        The address of the redeeming account
     * @param  _quantity    The number of sets to burn from redeemer
     */
    function burn(
        address _from,
        uint256 _quantity
    )
        external
    {
        // Check that function caller is Core
        require(
            msg.sender == ISetFactory(factory).core(),
            "SetToken.burn: Sender must be core"
        );

        _burn(_from, _quantity);
    }

    /*
     * Get addresses of all components in the Set
     *
     * @return  componentAddresses       Array of component tokens
     */
    function getComponents()
        external
        view
        returns(address[] memory)
    {
        address[] memory componentAddresses = new address[](components.length);

        // Iterate through components and get address of each component
        for (uint256 i = 0; i < components.length; i++) {
            componentAddresses[i] = components[i].address_;
        }
        return componentAddresses;
    }

    /*
     * Get units of all tokens in Set
     *
     * @return  units       Array of component units
     */
    function getUnits()
        external
        view
        returns(uint256[] memory)
    {
        uint256[] memory units = new uint256[](components.length);

        // Iterate through components and get units of each component
        for (uint256 i = 0; i < components.length; i++) {
            units[i] = components[i].unit_;
        }
        return units;
    }

    /*
     * Validates address is member of Set's components
     *
     * @param  _tokenAddress     Address of token being checked
     * @return  bool             Whether token is member of Set's components
     */
    function tokenIsComponent(
        address _tokenAddress
    )
        public
        view
        returns (bool)
    {
        return isComponent[_tokenAddress];
    }
}