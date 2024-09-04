contract Refinement {

    struct StateOld {
        mapping (address => bool) _whitelisteds;
        address owner;


    }
    struct StateNew {
        mapping (address => bool) whitelist;
        uint length;
        address owner;
    }

    StateOld od;
    StateOld od_old;
    StateNew nw;
    StateNew nw_old;


    /// @notice precondition true
    /// @notice postcondition true
    function addWhitelisted_pre() public {}

    /// @notice precondition __verifier_eq(od._whitelisteds, nw.whitelist)
    /// @notice precondition (account == msg.sender && od._whitelisteds[account] == true && success) || (!success)
    /// @notice postcondition (account == msg.sender && nw.whitelist[account] == true && success) || (!success)
    function addWhitelisted_post(address account, bool success) public {}


    /// @notice precondition true
    /// @notice postcondition true
    function removeWhitelisted_pre() public {}

    /// @notice precondition __verifier_eq(od._whitelisteds, nw.whitelist)
    /// @notice precondition (account == msg.sender && od._whitelisteds[account] == false && success) || (!success)
    /// @notice postcondition (account == msg.sender && nw.whitelist[account] == false && success) || (!success)
    function removeWhitelisted_post(address account, bool success) public {}




}