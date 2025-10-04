// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "./interfaces/IPriceOracle.sol";

/**
 * @title OnchainAgents
 * @notice Fully onchain AI trading agents with embedded analysis logic
 * @dev Complete onchain implementation of Yuki, Ryu, and Sakura agents
 */
contract OnchainAgents is ReentrancyGuard, Ownable, Pausable {

    // Agent Types
    enum AgentType { YUKI, RYU, SAKURA }

    // Market Data Sources
    enum DataSource { CHAINLINK, UNISWAP_V3, COMPOUND, AAVE }

    // Trading Strategies
    enum Strategy {
        MOMENTUM_LONG,
        MOMENTUM_SHORT,
        MEAN_REVERSION,
        YIELD_FARMING,
        ARBITRAGE
    }

    // Risk Levels
    enum RiskLevel { LOW, MEDIUM, HIGH, EXTREME }

    // Agent Analysis Result
    struct AnalysisResult {
        AgentType agent;
        Strategy recommendedStrategy;
        RiskLevel riskLevel;
        uint256 confidence; // 0-100
        uint256 entryPrice;
        uint256 targetPrice;
        uint256 stopLoss;
        uint256 timeHorizon; // seconds
        uint256 timestamp;
        bool isValid;
    }

    // Market Data Point
    struct MarketData {
        uint256 price;
        uint256 volume24h;
        uint256 volatility; // basis points
        uint256 rsi; // 0-100
        uint256 macd; // scaled by 1e18
        uint256 timestamp;
        bool isValid;
    }


    // Storage
    mapping(string => MarketData) public marketData;
    mapping(AgentType => uint256) public agentSuccessRate;
    mapping(address => mapping(AgentType => uint256)) public userAnalysisCount;
    mapping(bytes32 => AnalysisResult) public analysisResults;

    IPriceOracle public priceOracle;

    // Agent Parameters
    struct AgentConfig {
        uint256 minConfidence;
        uint256 maxRiskTolerance;
        uint256 analysisFeeBasisPoints;
        bool isActive;
    }

    mapping(AgentType => AgentConfig) public agentConfigs;

    // Events
    event AnalysisRequested(
        address indexed user,
        AgentType indexed agent,
        string symbol,
        bytes32 analysisId
    );

    event AnalysisCompleted(
        bytes32 indexed analysisId,
        AgentType indexed agent,
        Strategy strategy,
        uint256 confidence
    );

    event MarketDataUpdated(
        string indexed symbol,
        uint256 price,
        uint256 volume,
        uint256 timestamp
    );

    constructor(address _priceOracle) {
        priceOracle = IPriceOracle(_priceOracle);

        // Initialize agent configurations
        agentConfigs[AgentType.YUKI] = AgentConfig({
            minConfidence: 70,
            maxRiskTolerance: 90,
            analysisFeeBasisPoints: 50, // 0.5%
            isActive: true
        });

        agentConfigs[AgentType.RYU] = AgentConfig({
            minConfidence: 60,
            maxRiskTolerance: 60,
            analysisFeeBasisPoints: 25, // 0.25%
            isActive: true
        });

        agentConfigs[AgentType.SAKURA] = AgentConfig({
            minConfidence: 50,
            maxRiskTolerance: 30,
            analysisFeeBasisPoints: 15, // 0.15%
            isActive: true
        });
    }

    /**
     * @notice Request onchain agent analysis
     * @param agent The agent type to use
     * @param symbol The trading symbol to analyze
     * @param amount The amount to analyze for (for fee calculation)
     */
    function requestAnalysis(
        AgentType agent,
        string memory symbol,
        uint256 amount
    ) external payable nonReentrant returns (bytes32) {
        require(agentConfigs[agent].isActive, "Agent not active");

        // Calculate and require analysis fee
        uint256 fee = (amount * agentConfigs[agent].analysisFeeBasisPoints) / 10000;
        require(msg.value >= fee, "Insufficient analysis fee");

        bytes32 analysisId = keccak256(abi.encodePacked(
            msg.sender,
            agent,
            symbol,
            block.timestamp,
            block.number
        ));

        // Get fresh market data
        _updateMarketData(symbol);

        // Execute onchain analysis
        AnalysisResult memory result = _executeOnchainAnalysis(agent, symbol);
        result.timestamp = block.timestamp;

        analysisResults[analysisId] = result;
        userAnalysisCount[msg.sender][agent]++;

        emit AnalysisRequested(msg.sender, agent, symbol, analysisId);
        emit AnalysisCompleted(analysisId, agent, result.recommendedStrategy, result.confidence);

        return analysisId;
    }

    /**
     * @notice Execute onchain analysis using embedded agent logic
     * @param agent The agent type
     * @param symbol The symbol to analyze
     */
    function _executeOnchainAnalysis(
        AgentType agent,
        string memory symbol
    ) internal view returns (AnalysisResult memory) {
        MarketData memory data = marketData[symbol];
        require(data.isValid, "Invalid market data");

        if (agent == AgentType.YUKI) {
            return _yukiAnalysis(data);
        } else if (agent == AgentType.RYU) {
            return _ryuAnalysis(data);
        } else {
            return _sakuraAnalysis(data);
        }
    }

    /**
     * @notice Yuki Agent - Aggressive momentum trading
     */
    function _yukiAnalysis(MarketData memory data) internal pure returns (AnalysisResult memory) {
        AnalysisResult memory result;
        result.agent = AgentType.YUKI;
        result.isValid = true;

        // Yuki's aggressive momentum logic
        if (data.rsi < 30 && data.macd > 0 && data.volatility > 500) {
            // Strong oversold with bullish momentum + high volatility
            result.recommendedStrategy = Strategy.MOMENTUM_LONG;
            result.confidence = 85;
            result.riskLevel = RiskLevel.HIGH;
            result.entryPrice = data.price;
            result.targetPrice = data.price * 110 / 100; // 10% target
            result.stopLoss = data.price * 95 / 100; // 5% stop
            result.timeHorizon = 4 hours;
        } else if (data.rsi > 70 && data.macd < 0 && data.volatility > 500) {
            // Strong overbought with bearish momentum + high volatility
            result.recommendedStrategy = Strategy.MOMENTUM_SHORT;
            result.confidence = 80;
            result.riskLevel = RiskLevel.HIGH;
            result.entryPrice = data.price;
            result.targetPrice = data.price * 90 / 100; // 10% target down
            result.stopLoss = data.price * 105 / 100; // 5% stop
            result.timeHorizon = 4 hours;
        } else if (data.volatility > 800) {
            // Very high volatility - momentum play
            result.recommendedStrategy = data.rsi < 50 ? Strategy.MOMENTUM_LONG : Strategy.MOMENTUM_SHORT;
            result.confidence = 75;
            result.riskLevel = RiskLevel.EXTREME;
            result.entryPrice = data.price;
            result.targetPrice = data.rsi < 50 ? data.price * 108 / 100 : data.price * 92 / 100;
            result.stopLoss = data.rsi < 50 ? data.price * 97 / 100 : data.price * 103 / 100;
            result.timeHorizon = 2 hours;
        } else {
            // Low confidence signal
            result.recommendedStrategy = Strategy.MOMENTUM_LONG;
            result.confidence = 45;
            result.riskLevel = RiskLevel.MEDIUM;
            result.entryPrice = data.price;
            result.targetPrice = data.price * 103 / 100;
            result.stopLoss = data.price * 98 / 100;
            result.timeHorizon = 8 hours;
        }

        return result;
    }

    /**
     * @notice Ryu Agent - Balanced technical analysis
     */
    function _ryuAnalysis(MarketData memory data) internal pure returns (AnalysisResult memory) {
        AnalysisResult memory result;
        result.agent = AgentType.RYU;
        result.isValid = true;

        // Ryu's balanced approach
        uint256 signalStrength = 0;

        // RSI analysis
        if (data.rsi < 35) signalStrength += 25; // Oversold
        else if (data.rsi > 65) signalStrength += 20; // Overbought
        else signalStrength += 10; // Neutral

        // MACD analysis
        if (data.macd > 0) signalStrength += 20; // Bullish
        else if (data.macd < 0) signalStrength += 15; // Bearish

        // Volatility analysis
        if (data.volatility > 300 && data.volatility < 600) signalStrength += 20; // Good volatility
        else if (data.volatility > 600) signalStrength += 10; // Too volatile
        else signalStrength += 5; // Too stable

        // Volume analysis (simplified)
        if (data.volume24h > 1000000 ether) signalStrength += 15; // High volume
        else signalStrength += 5;

        result.confidence = signalStrength;

        if (signalStrength >= 70) {
            if (data.rsi < 40 && data.macd > 0) {
                result.recommendedStrategy = Strategy.MOMENTUM_LONG;
                result.riskLevel = RiskLevel.MEDIUM;
                result.targetPrice = data.price * 105 / 100; // 5% target
                result.stopLoss = data.price * 97 / 100; // 3% stop
            } else if (data.rsi > 60 && data.macd < 0) {
                result.recommendedStrategy = Strategy.MOMENTUM_SHORT;
                result.riskLevel = RiskLevel.MEDIUM;
                result.targetPrice = data.price * 95 / 100; // 5% target
                result.stopLoss = data.price * 103 / 100; // 3% stop
            } else {
                result.recommendedStrategy = Strategy.MEAN_REVERSION;
                result.riskLevel = RiskLevel.LOW;
                result.targetPrice = data.price * 102 / 100; // 2% target
                result.stopLoss = data.price * 99 / 100; // 1% stop
            }
            result.timeHorizon = 12 hours;
        } else {
            // Conservative approach
            result.recommendedStrategy = Strategy.MEAN_REVERSION;
            result.riskLevel = RiskLevel.LOW;
            result.targetPrice = data.price * 101 / 100; // 1% target
            result.stopLoss = data.price * 995 / 1000; // 0.5% stop
            result.timeHorizon = 24 hours;
        }

        result.entryPrice = data.price;
        return result;
    }

    /**
     * @notice Sakura Agent - Conservative yield farming
     */
    function _sakuraAnalysis(MarketData memory data) internal pure returns (AnalysisResult memory) {
        AnalysisResult memory result;
        result.agent = AgentType.SAKURA;
        result.isValid = true;
        result.recommendedStrategy = Strategy.YIELD_FARMING;
        result.riskLevel = RiskLevel.LOW;
        result.entryPrice = data.price;
        result.timeHorizon = 30 days;

        // Sakura focuses on stable yields, not price speculation
        if (data.volatility < 200) {
            // Low volatility = good for yield farming
            result.confidence = 80;
            result.targetPrice = data.price * 103 / 100; // 3% yield target
            result.stopLoss = data.price * 98 / 100; // 2% risk
        } else if (data.volatility < 400) {
            // Medium volatility
            result.confidence = 60;
            result.targetPrice = data.price * 102 / 100; // 2% yield target
            result.stopLoss = data.price * 99 / 100; // 1% risk
        } else {
            // High volatility - wait for stability
            result.confidence = 30;
            result.targetPrice = data.price * 101 / 100; // 1% yield target
            result.stopLoss = data.price * 995 / 1000; // 0.5% risk
        }

        return result;
    }

    /**
     * @notice Update market data from onchain sources
     */
    function _updateMarketData(string memory symbol) internal {
        try priceOracle.getPrice(symbol) returns (uint256 price) {
            uint256 volume = priceOracle.getVolume24h(symbol);
            uint256 volatility = priceOracle.getVolatility(symbol);

            MarketData storage data = marketData[symbol];

            // Calculate RSI (simplified onchain version)
            uint256 rsi = _calculateRSI(data.price, price);

            // Calculate MACD (simplified onchain version)
            int256 macd = _calculateMACD(data.price, price);

            data.price = price;
            data.volume24h = volume;
            data.volatility = volatility;
            data.rsi = rsi;
            data.macd = uint256(macd);
            data.timestamp = block.timestamp;
            data.isValid = true;

            emit MarketDataUpdated(symbol, price, volume, block.timestamp);
        } catch {
            // Handle oracle failure
            revert("Failed to update market data");
        }
    }

    /**
     * @notice Calculate RSI (simplified onchain version)
     */
    function _calculateRSI(uint256 prevPrice, uint256 currentPrice) internal pure returns (uint256) {
        if (prevPrice == 0) return 50; // Neutral RSI

        if (currentPrice > prevPrice) {
            uint256 gain = ((currentPrice - prevPrice) * 100) / prevPrice;
            return 50 + (gain * 10); // Simplified RSI calculation
        } else if (currentPrice < prevPrice) {
            uint256 loss = ((prevPrice - currentPrice) * 100) / prevPrice;
            return 50 - (loss * 10); // Simplified RSI calculation
        }

        return 50; // No change
    }

    /**
     * @notice Calculate MACD (simplified onchain version)
     */
    function _calculateMACD(uint256 prevPrice, uint256 currentPrice) internal pure returns (int256) {
        if (prevPrice == 0) return 0;

        if (currentPrice > prevPrice) {
            return int256(((currentPrice - prevPrice) * 1e18) / prevPrice);
        } else {
            return -int256(((prevPrice - currentPrice) * 1e18) / prevPrice);
        }
    }

    /**
     * @notice Get analysis result
     */
    function getAnalysisResult(bytes32 analysisId) external view returns (AnalysisResult memory) {
        return analysisResults[analysisId];
    }

    /**
     * @notice Get current market data
     */
    function getMarketData(string memory symbol) external view returns (MarketData memory) {
        return marketData[symbol];
    }

    /**
     * @notice Admin functions
     */
    function updateAgentConfig(
        AgentType agent,
        uint256 minConfidence,
        uint256 maxRiskTolerance,
        uint256 analysisFeeBasisPoints,
        bool isActive
    ) external onlyOwner {
        agentConfigs[agent] = AgentConfig({
            minConfidence: minConfidence,
            maxRiskTolerance: maxRiskTolerance,
            analysisFeeBasisPoints: analysisFeeBasisPoints,
            isActive: isActive
        });
    }

    function updatePriceOracle(address _priceOracle) external onlyOwner {
        priceOracle = IPriceOracle(_priceOracle);
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function withdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}