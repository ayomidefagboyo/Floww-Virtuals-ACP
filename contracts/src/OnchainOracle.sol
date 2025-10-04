// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./interfaces/IChainlinkAggregator.sol";
import "./interfaces/IUniswapV3Pool.sol";

/**
 * @title OnchainOracle
 * @notice Aggregated onchain oracle for market data
 * @dev Combines Chainlink, Uniswap V3, and other onchain sources
 */
contract OnchainOracle is Ownable, ReentrancyGuard {


    // Market Data Structure
    struct MarketDataPoint {
        uint256 price;          // Price in USD (18 decimals)
        uint256 volume24h;      // 24h volume in USD
        uint256 volatility;     // Volatility in basis points
        uint256 liquidity;      // Total liquidity
        uint256 timestamp;
        bool isValid;
    }

    // Price Source Configuration
    struct PriceSource {
        address chainlinkFeed;
        address uniswapPool;
        uint256 weight;         // Weight in basis points (total should be 10000)
        bool isActive;
    }

    // Storage
    mapping(string => PriceSource) public priceSources;
    mapping(string => MarketDataPoint) public marketData;
    mapping(string => uint256[]) private priceHistory; // For volatility calculation

    uint256 public constant VOLATILITY_WINDOW = 24; // 24 data points for volatility
    uint256 public constant MAX_PRICE_AGE = 3600; // 1 hour max age

    // Events
    event PriceUpdated(string indexed symbol, uint256 price, uint256 timestamp);
    event PriceSourceAdded(string indexed symbol, address chainlinkFeed, address uniswapPool);
    event MarketDataRefreshed(string indexed symbol, uint256 price, uint256 volume, uint256 volatility);

    constructor() {}

    /**
     * @notice Add price source for a symbol
     */
    function addPriceSource(
        string memory symbol,
        address chainlinkFeed,
        address uniswapPool,
        uint256 weight
    ) external onlyOwner {
        require(weight > 0 && weight <= 10000, "Invalid weight");

        priceSources[symbol] = PriceSource({
            chainlinkFeed: chainlinkFeed,
            uniswapPool: uniswapPool,
            weight: weight,
            isActive: true
        });

        emit PriceSourceAdded(symbol, chainlinkFeed, uniswapPool);
    }

    /**
     * @notice Get aggregated price from multiple sources
     */
    function getPrice(string memory symbol) external view returns (uint256) {
        return _getAggregatedPrice(symbol);
    }

    /**
     * @notice Get 24h volume
     */
    function getVolume24h(string memory symbol) external view returns (uint256) {
        MarketDataPoint memory data = marketData[symbol];
        require(data.isValid && block.timestamp - data.timestamp < MAX_PRICE_AGE, "Stale data");
        return data.volume24h;
    }

    /**
     * @notice Get volatility (basis points)
     */
    function getVolatility(string memory symbol) external view returns (uint256) {
        MarketDataPoint memory data = marketData[symbol];
        require(data.isValid && block.timestamp - data.timestamp < MAX_PRICE_AGE, "Stale data");
        return data.volatility;
    }

    /**
     * @notice Update market data for a symbol
     */
    function updateMarketData(string memory symbol) external nonReentrant {
        uint256 price = _getAggregatedPrice(symbol);
        uint256 volume = _getUniswapVolume(symbol);
        uint256 volatility = _calculateVolatility(symbol, price);
        uint256 liquidity = _getUniswapLiquidity(symbol);

        marketData[symbol] = MarketDataPoint({
            price: price,
            volume24h: volume,
            volatility: volatility,
            liquidity: liquidity,
            timestamp: block.timestamp,
            isValid: true
        });

        // Update price history for volatility calculation
        _updatePriceHistory(symbol, price);

        emit MarketDataRefreshed(symbol, price, volume, volatility);
        emit PriceUpdated(symbol, price, block.timestamp);
    }

    /**
     * @notice Get aggregated price from Chainlink and Uniswap
     */
    function _getAggregatedPrice(string memory symbol) internal view returns (uint256) {
        PriceSource memory source = priceSources[symbol];
        require(source.isActive, "Price source not active");

        uint256 totalWeight = 0;
        uint256 weightedPrice = 0;

        // Get Chainlink price
        if (source.chainlinkFeed != address(0)) {
            try IChainlinkAggregator(source.chainlinkFeed).latestRoundData() returns (
                uint80,
                int256 price,
                uint256,
                uint256 updatedAt,
                uint80
            ) {
                require(block.timestamp - updatedAt < MAX_PRICE_AGE, "Chainlink data too old");
                require(price > 0, "Invalid Chainlink price");

                uint8 decimals = IChainlinkAggregator(source.chainlinkFeed).decimals();
                uint256 normalizedPrice = uint256(price) * (10**(18 - decimals));

                weightedPrice += normalizedPrice * 5000; // 50% weight for Chainlink
                totalWeight += 5000;
            } catch {
                // Chainlink failed, continue with Uniswap only
            }
        }

        // Get Uniswap price
        if (source.uniswapPool != address(0)) {
            try this._getUniswapPrice(source.uniswapPool) returns (uint256 uniPrice) {
                weightedPrice += uniPrice * 5000; // 50% weight for Uniswap
                totalWeight += 5000;
            } catch {
                // Uniswap failed
            }
        }

        require(totalWeight > 0, "No valid price sources");
        return weightedPrice / totalWeight;
    }

    /**
     * @notice Get Uniswap V3 price (external for try/catch)
     */
    function _getUniswapPrice(address pool) external view returns (uint256) {
        (uint160 sqrtPriceX96,,,,,,) = IUniswapV3Pool(pool).slot0();

        // Convert sqrtPriceX96 to price
        // price = (sqrtPriceX96 / 2^96)^2
        uint256 price = (uint256(sqrtPriceX96) * uint256(sqrtPriceX96) * 1e18) >> (96 * 2);

        return price;
    }

    /**
     * @notice Calculate volume from Uniswap (simplified)
     */
    function _getUniswapVolume(string memory symbol) internal view returns (uint256) {
        PriceSource memory source = priceSources[symbol];

        if (source.uniswapPool == address(0)) {
            return 1000000 * 1e18; // Default volume
        }

        // Simplified: use liquidity as proxy for volume
        try IUniswapV3Pool(source.uniswapPool).liquidity() returns (uint128 liquidity) {
            return uint256(liquidity) * 100; // Rough approximation
        } catch {
            return 1000000 * 1e18; // Default volume
        }
    }

    /**
     * @notice Get liquidity from Uniswap pool
     */
    function _getUniswapLiquidity(string memory symbol) internal view returns (uint256) {
        PriceSource memory source = priceSources[symbol];

        if (source.uniswapPool == address(0)) {
            return 10000000 * 1e18; // Default liquidity
        }

        try IUniswapV3Pool(source.uniswapPool).liquidity() returns (uint128 liquidity) {
            return uint256(liquidity);
        } catch {
            return 10000000 * 1e18; // Default liquidity
        }
    }

    /**
     * @notice Calculate volatility based on price history
     */
    function _calculateVolatility(string memory symbol, uint256 currentPrice) internal view returns (uint256) {
        uint256[] memory history = priceHistory[symbol];

        if (history.length < 2) {
            return 500; // Default volatility (5%)
        }

        uint256 sumSquaredReturns = 0;
        uint256 count = 0;

        // Calculate returns and their variance
        for (uint256 i = 1; i < history.length && i < VOLATILITY_WINDOW; i++) {
            if (history[i-1] > 0) {
                int256 return_ = int256((history[i] * 10000) / history[i-1]) - 10000;
                sumSquaredReturns += uint256(return_ * return_);
                count++;
            }
        }

        if (count == 0) {
            return 500; // Default volatility
        }

        // Simplified volatility calculation (standard deviation of returns)
        uint256 variance = sumSquaredReturns / count;
        uint256 volatility = sqrt(variance);

        // Cap volatility between 1% and 50%
        return volatility < 100 ? 100 : (volatility > 5000 ? 5000 : volatility);
    }

    /**
     * @notice Update price history for volatility calculation
     */
    function _updatePriceHistory(string memory symbol, uint256 price) internal {
        uint256[] storage history = priceHistory[symbol];

        history.push(price);

        // Keep only last VOLATILITY_WINDOW prices
        if (history.length > VOLATILITY_WINDOW) {
            // Remove first element by shifting array
            for (uint256 i = 0; i < history.length - 1; i++) {
                history[i] = history[i + 1];
            }
            history.pop();
        }
    }

    /**
     * @notice Square root function for volatility calculation
     */
    function sqrt(uint256 x) internal pure returns (uint256) {
        if (x == 0) return 0;

        uint256 z = (x + 1) / 2;
        uint256 y = x;

        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }

        return y;
    }

    /**
     * @notice Batch update multiple symbols
     */
    function batchUpdateMarketData(string[] memory symbols) external {
        for (uint256 i = 0; i < symbols.length; i++) {
            try this.updateMarketData(symbols[i]) {
                // Success
            } catch {
                // Continue with next symbol
            }
        }
    }

    /**
     * @notice Emergency functions
     */
    function deactivatePriceSource(string memory symbol) external onlyOwner {
        priceSources[symbol].isActive = false;
    }

    function activatePriceSource(string memory symbol) external onlyOwner {
        priceSources[symbol].isActive = true;
    }

    /**
     * @notice Get market data
     */
    function getMarketData(string memory symbol) external view returns (MarketDataPoint memory) {
        return marketData[symbol];
    }
}