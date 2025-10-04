// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IChainlinkAggregator
 * @notice Chainlink price feed interface
 */
interface IChainlinkAggregator {
    function latestRoundData() external view returns (
        uint80 roundId,
        int256 price,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    );
    function decimals() external view returns (uint8);
}