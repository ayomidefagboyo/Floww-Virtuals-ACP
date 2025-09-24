// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/VirtualsACP.sol";

/**
 * @title DeployVirtualsACP
 * @notice Deployment script for Virtuals Agent Commerce Protocol contract
 * @dev Deploys to Base Sepolia (testnet) first, then Base Mainnet
 */
contract DeployVirtualsACP is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);

        console.log("Deploying VirtualsACP contract...");
        console.log("Deployer address:", deployer);
        console.log("Deployer balance:", deployer.balance);
        console.log("Chain ID:", block.chainid);

        vm.startBroadcast(deployerPrivateKey);

        // Deploy VirtualsACP contract
        VirtualsACP virtualsACP = new VirtualsACP();

        console.log("VirtualsACP deployed at:", address(virtualsACP));

        // Verify deployment
        require(address(virtualsACP) != address(0), "Deployment failed");
        require(virtualsACP.owner() == deployer, "Owner not set correctly");

        console.log("VirtualsACP deployment successful!");
        console.log("Contract address:", address(virtualsACP));
        console.log("Owner:", virtualsACP.owner());

        vm.stopBroadcast();

        // Save deployment info
        _saveDeploymentInfo(address(virtualsACP));
    }

    function _saveDeploymentInfo(address contractAddress) internal {
        string memory networkName = _getNetworkName();
        string memory deploymentInfo = string(abi.encodePacked(
            "// VirtualsACP Deployment Info\n",
            "// Network: ", networkName, "\n",
            "// Contract Address: ", vm.toString(contractAddress), "\n",
            "// Deployed at: ", vm.toString(block.timestamp), "\n",
            "// Chain ID: ", vm.toString(block.chainid), "\n",
            "// Deployer: ", vm.toString(msg.sender), "\n\n"
        ));

        vm.writeFile(
            string(abi.encodePacked("./deployments/VirtualsACP_", networkName, ".txt")),
            deploymentInfo
        );
    }

    function _getNetworkName() internal view returns (string memory) {
        if (block.chainid == 8453) return "Base_Mainnet";
        if (block.chainid == 84532) return "Base_Sepolia";
        if (block.chainid == 31337) return "Local_Anvil";
        return "Unknown";
    }
}