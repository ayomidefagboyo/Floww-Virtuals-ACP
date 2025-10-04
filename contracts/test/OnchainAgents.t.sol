// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/OnchainAgents.sol";
import "../src/OnchainOracle.sol";

contract OnchainAgentsTest is Test {
    OnchainAgents public agents;
    OnchainOracle public oracle;
    address public user = address(0x123);

    function setUp() public {
        // Deploy oracle first
        oracle = new OnchainOracle();

        // Deploy agents with oracle address
        agents = new OnchainAgents(address(oracle));

        // Fund user account
        vm.deal(user, 10 ether);

        // Add a test price source
        oracle.addPriceSource("BTC", address(0), address(0), 10000);

        // Manually set market data for testing
        vm.prank(address(oracle));
        oracle.updateMarketData("BTC");
    }

    function testYukiAnalysis() public {
        vm.startPrank(user);

        uint256 amount = 1000 ether;
        uint256 fee = 0.005 ether; // 0.5% of amount

        bytes32 analysisId = agents.requestAnalysis{value: fee}(
            OnchainAgents.AgentType.YUKI,
            "BTC",
            amount
        );

        // Verify analysis was created
        OnchainAgents.AnalysisResult memory result = agents.getAnalysisResult(analysisId);
        assertTrue(result.isValid);
        assertEq(uint8(result.agent), uint8(OnchainAgents.AgentType.YUKI));
        assertGt(result.confidence, 0);

        vm.stopPrank();
    }

    function testRyuAnalysis() public {
        vm.startPrank(user);

        uint256 amount = 1000 ether;
        uint256 fee = 0.0025 ether; // 0.25% of amount

        bytes32 analysisId = agents.requestAnalysis{value: fee}(
            OnchainAgents.AgentType.RYU,
            "BTC",
            amount
        );

        // Verify analysis was created
        OnchainAgents.AnalysisResult memory result = agents.getAnalysisResult(analysisId);
        assertTrue(result.isValid);
        assertEq(uint8(result.agent), uint8(OnchainAgents.AgentType.RYU));
        assertGt(result.confidence, 0);

        vm.stopPrank();
    }

    function testSakuraAnalysis() public {
        vm.startPrank(user);

        uint256 amount = 1000 ether;
        uint256 fee = 0.0015 ether; // 0.15% of amount

        bytes32 analysisId = agents.requestAnalysis{value: fee}(
            OnchainAgents.AgentType.SAKURA,
            "BTC",
            amount
        );

        // Verify analysis was created
        OnchainAgents.AnalysisResult memory result = agents.getAnalysisResult(analysisId);
        assertTrue(result.isValid);
        assertEq(uint8(result.agent), uint8(OnchainAgents.AgentType.SAKURA));
        assertGt(result.confidence, 0);
        assertEq(uint8(result.recommendedStrategy), uint8(OnchainAgents.Strategy.YIELD_FARMING));

        vm.stopPrank();
    }

    function testInsufficientFee() public {
        vm.startPrank(user);

        uint256 amount = 1000 ether;
        uint256 insufficientFee = 0.001 ether; // Less than required 0.5%

        vm.expectRevert("Insufficient analysis fee");
        agents.requestAnalysis{value: insufficientFee}(
            OnchainAgents.AgentType.YUKI,
            "BTC",
            amount
        );

        vm.stopPrank();
    }

    function testGetMarketData() public {
        OnchainAgents.MarketData memory data = agents.getMarketData("BTC");

        // Should have default values since we don't have real price feeds
        assertGt(data.price, 0);
    }

    function testAgentConfigs() public {
        (uint256 yukiMin, uint256 yukiRisk, uint256 yukiFee, bool yukiActive) = agents.agentConfigs(OnchainAgents.AgentType.YUKI);
        assertEq(yukiMin, 70);
        assertEq(yukiFee, 50);
        assertTrue(yukiActive);

        (uint256 ryuMin, uint256 ryuRisk, uint256 ryuFee, bool ryuActive) = agents.agentConfigs(OnchainAgents.AgentType.RYU);
        assertEq(ryuMin, 60);
        assertEq(ryuFee, 25);

        (uint256 sakuraMin, uint256 sakuraRisk, uint256 sakuraFee, bool sakuraActive) = agents.agentConfigs(OnchainAgents.AgentType.SAKURA);
        assertEq(sakuraMin, 50);
        assertEq(sakuraFee, 15);
    }
}