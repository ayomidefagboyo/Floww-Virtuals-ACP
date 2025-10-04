// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/FlowAgentVault.sol";
import "../src/SakuraPendleVault.sol";
import "../src/HyperliquidVault.sol";
import "../src/AgentExecutor.sol";
import "./FlowAgentVault.t.sol"; // Import mocks

/**
 * @title Integration Test
 * @notice End-to-end integration tests for the complete Flow AI Agent Delegation System
 */
contract IntegrationTest is Test {
    // Core contracts
    FlowAgentVault public vault;
    SakuraPendleVault public sakuraVault;
    HyperliquidVault public hyperliquidVault;
    AgentExecutor public executor;

    // Mock contracts
    MockUSDC public usdc;
    MockWETH public weth;
    MockUniswapV3Router public router;

    // Test accounts
    address public owner = address(this);
    address public treasury = address(0x1);
    address public backend = address(0x2);
    address public user1 = address(0x3);
    address public user2 = address(0x4);

    // Test constants
    uint256 constant INITIAL_ETH = 10 ether;
    uint256 constant PLATFORM_FEE = 50; // 0.5%
    uint256 constant MIN_DELEGATION = 100e6; // $100

    function setUp() public {
        // Deploy mock infrastructure
        usdc = new MockUSDC();
        weth = new MockWETH();
        router = new MockUniswapV3Router(address(usdc), address(weth));

        // Deploy core contracts
        sakuraVault = new SakuraPendleVault();
        hyperliquidVault = new HyperliquidVault(address(0)); // Will be updated

        vault = new FlowAgentVault(
            address(usdc),
            address(weth),
            address(router),
            treasury
        );

        // Update HyperliquidVault with correct main vault
        hyperliquidVault = new HyperliquidVault(address(vault));

        executor = new AgentExecutor(
            address(vault),
            address(sakuraVault),
            address(hyperliquidVault)
        );

        // Configure system
        vault.setVaultAddresses(address(sakuraVault), address(hyperliquidVault));
        vault.setPlatformFee(PLATFORM_FEE);
        vault.setMinDelegationAmount(MIN_DELEGATION);

        sakuraVault.setMainVault(address(vault));
        executor.setBackendAuthorization(backend, true);

        // Setup test accounts
        vm.deal(user1, INITIAL_ETH);
        vm.deal(user2, INITIAL_ETH);
        vm.deal(backend, 1 ether);

        // Mint USDC for router to simulate liquidity
        usdc.mint(address(router), 10000000e6); // 10M USDC
    }

    function testCompleteFlowSakuraJourney() public {
        // Test complete user journey with Sakura agent
        uint256 ethAmount = 2 ether;
        uint256 delegateAmount = 4000e6; // $4000
        uint256 minUSDCOut = 3800e6; // $3800 minimum

        console.log("=== Starting Complete Sakura Journey ===");

        // Step 1: User delegates to Sakura
        console.log("Step 1: User delegation");
        vm.startPrank(user1);

        uint256 initialBalance = user1.balance;
        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.SAKURA,
            delegateAmount,
            minUSDCOut
        );

        vm.stopPrank();

        // Verify delegation
        uint256 userBalance = vault.getUserBalance(user1, IFlowAgentVault.AgentType.SAKURA);
        assertGt(userBalance, 0, "User should have Sakura balance");
        assertGt(treasury.balance + usdc.balanceOf(treasury), 0, "Treasury should receive fees");

        console.log("   Delegated amount:", userBalance);
        console.log("   Gas preserved:", user1.balance);

        // Step 2: Backend executes strategy
        console.log("Step 2: Backend execution");
        address pendleMarket = address(0x123);
        sakuraVault.addApprovedMarket(pendleMarket);

        vm.prank(backend);
        executor.executeSakuraStrategy(user1, pendleMarket, 1000e6);

        // Verify execution
        uint256[] memory executions = executor.getUserExecutionHistory(user1);
        assertEq(executions.length, 1, "Should have one execution");

        AgentExecutor.ExecutionRecord memory record = executor.getExecutionRecord(executions[0]);
        assertTrue(record.success, "Execution should be successful");

        console.log("   Execution ID:", executions[0]);
        console.log("   Execution success:", record.success);

        // Step 3: User withdraws partial amount
        console.log("Step 3: Partial withdrawal");
        uint256 withdrawAmount = userBalance / 2;
        uint256 initialUSDCBalance = usdc.balanceOf(user1);

        vm.prank(user1);
        vault.withdraw(IFlowAgentVault.AgentType.SAKURA, withdrawAmount);

        uint256 finalBalance = vault.getUserBalance(user1, IFlowAgentVault.AgentType.SAKURA);
        uint256 finalUSDCBalance = usdc.balanceOf(user1);

        assertEq(finalBalance, userBalance - withdrawAmount, "Balance should decrease by withdrawal");
        assertGt(finalUSDCBalance, initialUSDCBalance, "User should receive USDC");

        console.log("   Withdrawn amount:", withdrawAmount);
        console.log("   Remaining balance:", finalBalance);

        // Step 4: User withdraws all remaining
        console.log("Step 4: Full withdrawal");
        vm.prank(user1);
        vault.withdrawAll(IFlowAgentVault.AgentType.SAKURA);

        uint256 zeroBalance = vault.getUserBalance(user1, IFlowAgentVault.AgentType.SAKURA);
        assertEq(zeroBalance, 0, "Balance should be zero after full withdrawal");

        console.log("   Final balance:", zeroBalance);
        console.log("=== Sakura Journey Complete ===");
    }

    function testMultiUserMultiAgentFlow() public {
        console.log("=== Multi-User Multi-Agent Flow ===");

        // User1 delegates to Sakura and RYU
        // User2 delegates to RYU and YUKI

        vm.startPrank(user1);

        // User1 -> Sakura
        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.SAKURA,
            2000e6,
            1900e6
        );

        // User1 -> RYU
        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.RYU,
            2000e6,
            1900e6
        );

        vm.stopPrank();

        vm.startPrank(user2);

        // User2 -> RYU
        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.RYU,
            2000e6,
            1900e6
        );

        // User2 -> YUKI
        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.YUKI,
            2000e6,
            1900e6
        );

        vm.stopPrank();

        // Verify all balances
        assertGt(vault.getUserBalance(user1, IFlowAgentVault.AgentType.SAKURA), 0, "User1 should have Sakura balance");
        assertGt(vault.getUserBalance(user1, IFlowAgentVault.AgentType.RYU), 0, "User1 should have RYU balance");
        assertGt(vault.getUserBalance(user2, IFlowAgentVault.AgentType.RYU), 0, "User2 should have RYU balance");
        assertGt(vault.getUserBalance(user2, IFlowAgentVault.AgentType.YUKI), 0, "User2 should have YUKI balance");

        console.log("User1 Sakura balance:", vault.getUserBalance(user1, IFlowAgentVault.AgentType.SAKURA));
        console.log("User1 RYU balance:", vault.getUserBalance(user1, IFlowAgentVault.AgentType.RYU));
        console.log("User2 RYU balance:", vault.getUserBalance(user2, IFlowAgentVault.AgentType.RYU));
        console.log("User2 YUKI balance:", vault.getUserBalance(user2, IFlowAgentVault.AgentType.YUKI));

        // Execute strategies for different agents
        vm.startPrank(backend);

        // Execute Sakura for User1
        address pendleMarket = address(0x123);
        sakuraVault.addApprovedMarket(pendleMarket);
        executor.executeSakuraStrategy(user1, pendleMarket, 500e6);

        // Execute RYU trades for both users
        executor.executeRyuTrade(
            user1,
            "ETH/USDC",
            IHyperliquidVault.TradeType.SPOT_BUY,
            500e6,
            2500e6
        );

        // Fast forward to bypass cooldown
        vm.warp(block.timestamp + 6 minutes);

        executor.executeRyuTrade(
            user2,
            "BTC/USDC",
            IHyperliquidVault.TradeType.SPOT_BUY,
            500e6,
            50000e6
        );

        // Execute YUKI futures for User2
        vm.warp(block.timestamp + 2 minutes);

        executor.executeYukiFutures(
            user2,
            "ETH/USD",
            IHyperliquidVault.TradeType.PERP_LONG,
            500e6,
            2500e6
        );

        vm.stopPrank();

        // Verify all executions
        assertEq(executor.getUserExecutionHistory(user1).length, 2, "User1 should have 2 executions");
        assertEq(executor.getUserExecutionHistory(user2).length, 2, "User2 should have 2 executions");

        console.log("Total User1 executions:", executor.getUserExecutionHistory(user1).length);
        console.log("Total User2 executions:", executor.getUserExecutionHistory(user2).length);

        console.log("=== Multi-User Flow Complete ===");
    }

    function testSystemLimitsAndSafety() public {
        console.log("=== Testing System Limits and Safety ===");

        // Test 1: Rate limiting
        address pendleMarket = address(0x123);
        sakuraVault.addApprovedMarket(pendleMarket);

        // Delegate first
        vm.prank(user1);
        vault.depositAndDelegate{value: 2 ether}(
            IFlowAgentVault.AgentType.SAKURA,
            4000e6,
            3800e6
        );

        vm.startPrank(backend);

        // First execution should work
        executor.executeSakuraStrategy(user1, pendleMarket, 1000e6);

        // Second execution should fail due to cooldown
        vm.expectRevert("Cooldown period not met");
        executor.executeSakuraStrategy(user1, pendleMarket, 1000e6);

        vm.stopPrank();

        // Test 2: Daily limits
        executor.setMaxDailyExecutions(IFlowAgentVault.AgentType.RYU, 1);

        vm.prank(user1);
        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.RYU,
            2000e6,
            1900e6
        );

        vm.startPrank(backend);

        // First RYU trade should work
        executor.executeRyuTrade(
            user1,
            "ETH/USDC",
            IHyperliquidVault.TradeType.SPOT_BUY,
            500e6,
            2500e6
        );

        // Fast forward past cooldown
        vm.warp(block.timestamp + 6 minutes);

        // Second trade should fail due to daily limit
        vm.expectRevert("Daily execution limit exceeded");
        executor.executeRyuTrade(
            user1,
            "ETH/USDC",
            IHyperliquidVault.TradeType.SPOT_BUY,
            500e6,
            2500e6
        );

        vm.stopPrank();

        // Test 3: Amount limits
        vm.startPrank(backend);

        vm.expectRevert("Amount exceeds limit");
        executor.executeSakuraStrategy(user1, pendleMarket, 60000e6); // Above $50k limit

        vm.stopPrank();

        // Test 4: Pause functionality
        vault.pause();

        vm.startPrank(user2);

        vm.expectRevert("Pausable: paused");
        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.SAKURA,
            2000e6,
            1900e6
        );

        vm.stopPrank();

        vault.unpause();

        // Should work after unpause
        vm.prank(user2);
        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.SAKURA,
            2000e6,
            1900e6
        );

        assertGt(vault.getUserBalance(user2, IFlowAgentVault.AgentType.SAKURA), 0, "Delegation should work after unpause");

        console.log("All safety mechanisms working correctly");
        console.log("=== Safety Tests Complete ===");
    }

    function testHyperliquidVaultFlow() public {
        console.log("=== Testing Hyperliquid Vault Flow ===");

        // Delegate to RYU agent
        vm.prank(user1);
        vault.depositAndDelegate{value: 2 ether}(
            IFlowAgentVault.AgentType.RYU,
            4000e6,
            3800e6
        );

        // Check HL account creation would be triggered
        uint256 userBalance = vault.getUserBalance(user1, IFlowAgentVault.AgentType.RYU);
        assertGt(userBalance, 0, "User should have RYU balance");

        // Simulate trade execution
        vm.prank(backend);
        executor.executeRyuTrade(
            user1,
            "ETH/USDC",
            IHyperliquidVault.TradeType.SPOT_BUY,
            1000e6,
            2500e6
        );

        // Verify execution was recorded
        uint256[] memory executions = executor.getUserExecutionHistory(user1);
        assertEq(executions.length, 1, "Should have one execution");

        AgentExecutor.ExecutionRecord memory record = executor.getExecutionRecord(executions[0]);
        assertEq(uint8(record.agentType), uint8(IFlowAgentVault.AgentType.RYU), "Should be RYU execution");

        console.log("Hyperliquid integration flow working");
        console.log("=== Hyperliquid Tests Complete ===");
    }

    function testGasOptimization() public {
        console.log("=== Gas Optimization Tests ===");

        uint256 gasStart;
        uint256 gasUsed;

        // Test delegation gas usage
        vm.prank(user1);
        gasStart = gasleft();

        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.SAKURA,
            2000e6,
            1900e6
        );

        gasUsed = gasStart - gasleft();
        console.log("Gas used for delegation:", gasUsed);

        // Test execution gas usage
        address pendleMarket = address(0x123);
        sakuraVault.addApprovedMarket(pendleMarket);

        vm.prank(backend);
        gasStart = gasleft();

        executor.executeSakuraStrategy(user1, pendleMarket, 500e6);

        gasUsed = gasStart - gasleft();
        console.log("Gas used for execution:", gasUsed);

        // Test withdrawal gas usage
        vm.prank(user1);
        gasStart = gasleft();

        vault.withdraw(IFlowAgentVault.AgentType.SAKURA, 500e6);

        gasUsed = gasStart - gasleft();
        console.log("Gas used for withdrawal:", gasUsed);

        console.log("=== Gas Tests Complete ===");
    }

    function testEventEmission() public {
        console.log("=== Event Emission Tests ===");

        // Test delegation event
        vm.expectEmit(true, true, false, true);
        emit IFlowAgentVault.FundsDelegated(user1, IFlowAgentVault.AgentType.SAKURA, 2000e6);

        vm.prank(user1);
        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.SAKURA,
            2000e6,
            1900e6
        );

        // Test execution events
        address pendleMarket = address(0x123);
        sakuraVault.addApprovedMarket(pendleMarket);

        vm.expectEmit(true, true, false, true);
        emit AgentExecutor.AgentExecutionCompleted(user1, IFlowAgentVault.AgentType.SAKURA, 0, true);

        vm.prank(backend);
        executor.executeSakuraStrategy(user1, pendleMarket, 500e6);

        console.log("All events emitted correctly");
        console.log("=== Event Tests Complete ===");
    }

    // Helper function to display system state
    function logSystemState() internal view {
        console.log("=== System State ===");
        console.log("Vault USDC balance:", usdc.balanceOf(address(vault)));
        console.log("Treasury USDC balance:", usdc.balanceOf(treasury));
        console.log("Sakura vault USDC balance:", usdc.balanceOf(address(sakuraVault)));
        console.log("Hyperliquid vault USDC balance:", usdc.balanceOf(address(hyperliquidVault)));
    }
}