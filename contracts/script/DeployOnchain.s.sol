// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "../src/OnchainAgents.sol";
import "../src/OnchainOracle.sol";

/**
 * @title Deploy Onchain Agents System
 * @notice Deployment script for fully onchain agent system
 */
contract DeployOnchain is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        // Deploy Oracle first
        OnchainOracle oracle = new OnchainOracle();
        console.log("OnchainOracle deployed at:", address(oracle));

        // Deploy Agents contract with Oracle address
        OnchainAgents agents = new OnchainAgents(address(oracle));
        console.log("OnchainAgents deployed at:", address(agents));

        // Configure some common price sources (for Base network)
        // Note: Replace these with actual Chainlink feed addresses for your network

        // BTC/USD Chainlink feed (example address - replace with actual)
        address btcUsdFeed = 0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70; // Base mainnet BTC/USD
        // ETH/USD Chainlink feed (example address - replace with actual)
        address ethUsdFeed = 0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70; // Base mainnet ETH/USD

        // Uniswap V3 pools (example addresses - replace with actual)
        address btcUsdcPool = 0x0000000000000000000000000000000000000000; // Replace
        address ethUsdcPool = 0x0000000000000000000000000000000000000000; // Replace

        // Add price sources
        oracle.addPriceSource("BTC", btcUsdFeed, btcUsdcPool, 10000);
        console.log("Added BTC price source");

        oracle.addPriceSource("ETH", ethUsdFeed, ethUsdcPool, 10000);
        console.log("Added ETH price source");

        // Update initial market data
        string[] memory symbols = new string[](2);
        symbols[0] = "BTC";
        symbols[1] = "ETH";

        oracle.batchUpdateMarketData(symbols);
        console.log("Initial market data updated");

        vm.stopBroadcast();

        // Log deployment information
        console.log("\n=== DEPLOYMENT COMPLETE ===");
        console.log("OnchainOracle:", address(oracle));
        console.log("OnchainAgents:", address(agents));
        console.log("\nUpdate your frontend with these contract addresses:");
        console.log("ONCHAIN_AGENTS_ADDRESS =", address(agents));
        console.log("ONCHAIN_ORACLE_ADDRESS =", address(oracle));
    }
}