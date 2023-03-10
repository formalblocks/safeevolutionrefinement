/*

    Copyright 2020 Kollateral LLC.

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

pragma solidity >= 0.5.0;


import "@openzeppelin/contracts/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../interfaces/SoloMarginLike.sol";
import "../interfaces/DYDXFlashBorrowerLike.sol";

contract SoloMarginMock is SoloMarginLike {
    using SafeMath for uint256;

    mapping(uint256 => address) internal _markets;

    constructor(uint256[] memory marketIds, address[] memory tokenAddresses) public {
        for (uint256 i = 0; i < marketIds.length; i++) {
            _markets[marketIds[i]] = tokenAddresses[i];
        }
    }

    function operate(DYDXDataTypes.AccountInfo[] memory accounts, DYDXDataTypes.ActionArgs[] memory actions) public  {
        /* data */
        require(accounts.length == 1, "SoloMarginMock: incorrect accounts length");
        require(actions.length == 3, "SoloMarginMock: incorrect actions length");

        /* withdraw */
        DYDXDataTypes.ActionArgs memory withdraw = actions[0];

        require(withdraw.amount.sign == false, "SoloMarginMock: incorrect withdraw sign");
        require(withdraw.amount.denomination == DYDXDataTypes.AssetDenomination.Wei, "SoloMarginMock: incorrect withdraw denomination");
        require(withdraw.amount.ref == DYDXDataTypes.AssetReference.Delta, "SoloMarginMock: incorrect withdraw reference");

        require(withdraw.actionType == DYDXDataTypes.ActionType.Withdraw, "SoloMarginMock: incorrect withdraw action type");

        /* call */
        DYDXDataTypes.ActionArgs memory call = actions[1];
        require(call.actionType == DYDXDataTypes.ActionType.Call, "SoloMarginMock: incorrect call action type");

        /* deposit */
        DYDXDataTypes.ActionArgs memory deposit = actions[2];
        require(withdraw.primaryMarketId == deposit.primaryMarketId, "SoloMarginMock: marketId mismatch");

        uint256 depositValue = withdraw.amount.value.add(repaymentFee(withdraw.primaryMarketId));
        require(deposit.amount.value == depositValue, "SoloMarginMock: incorrect deposit value");
        require(deposit.amount.sign == true, "SoloMarginMock: incorrect deposit sign");
        require(deposit.amount.denomination == DYDXDataTypes.AssetDenomination.Wei, "SoloMarginMock: incorrect deposit denomination");
        require(deposit.amount.ref == DYDXDataTypes.AssetReference.Delta, "SoloMarginMock: incorrect deposit reference");

        require(deposit.actionType == DYDXDataTypes.ActionType.Deposit, "SoloMarginMock: incorrect deposit action type");

        uint256 balanceBefore = balanceOf(withdraw.primaryMarketId);

        transfer(withdraw.primaryMarketId, msg.sender, withdraw.amount.value);

        DYDXFlashBorrowerLike(msg.sender).callFunction(msg.sender, DYDXDataTypes.AccountInfo({
            owner: accounts[0].owner,
            number: accounts[0].number
        }), call.data);

        transferFrom(deposit.primaryMarketId, msg.sender, address(this), deposit.amount.value);
        uint256 balanceAfter = balanceOf(withdraw.primaryMarketId);

        require(balanceAfter == balanceBefore.add(repaymentFee(withdraw.primaryMarketId)), "SoloMarginMock: Incorrect ending balance");
    }

    function getMarketTokenAddress(uint256 marketId) public view  returns (address) {
        return _markets[marketId];
    }

    function repaymentFee(uint256 marketId) internal returns (uint256) {
        return marketId < 2 ? 1 : 2;
    }

    function transfer(uint256 marketId, address to, uint256 amount) internal returns (bool) {
        return IERC20(_markets[marketId]).transfer(to, amount);
    }

    function transferFrom(uint256 marketId, address from, address to, uint256 amount) internal returns (bool) {
        return IERC20(_markets[marketId]).transferFrom(from, to, amount);
    }

    function balanceOf(uint256 marketId) internal view returns (uint256) {
            return IERC20(_markets[marketId]).balanceOf(address(this));
    }
}
