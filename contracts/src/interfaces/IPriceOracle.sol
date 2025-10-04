// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IPriceOracle
 * @notice Interface for onchain price oracle
 */
interface IPriceOracle {
    function getPrice(string memory symbol) external view returns (uint256);
    function getVolume24h(string memory symbol) external view returns (uint256);
    function getVolatility(string memory symbol) external view returns (uint256);
}