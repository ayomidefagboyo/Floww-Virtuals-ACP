// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/AgentExecutor.sol";
import "../src/FlowAgentVault.sol";
import "../src/SakuraPendleVault.sol";
import "../src/HyperliquidVault.sol";
import "./FlowAgentVault.t.sol"; // Import mocks

contract AgentExecutorTest is Test {
    AgentExecutor public executor;
    FlowAgentVault public vault;
    SakuraPendleVault public sakuraVault;
    HyperliquidVault public hyperliquidVault;
    MockUSDC public usdc;

    address public owner = address(this);
    address public backend = address(0x4);
    address public user = address(0x5);
    address public treasury = address(0x6);

    event AgentExecutionRequested(
        address indexed user,
        IFlowAgentVault.AgentType indexed agentType,
        bytes32 indexed actionHash,
        uint256 amount
    );

    event AgentExecutionCompleted(
        address indexed user,
        IFlowAgentVault.AgentType indexed agentType,
        uint256 executionId,
        bool success
    );

    function setUp() public {
        // Deploy mock USDC
        usdc = new MockUSDC();

        // Deploy vault contracts
        sakuraVault = new SakuraPendleVault();
        vault = new FlowAgentVault(
            address(usdc),
            address(0), // WETH not needed for executor tests
            address(0), // Router not needed for executor tests
            treasury
        );
        hyperliquidVault = new HyperliquidVault(address(vault));

        // Deploy executor
        executor = new AgentExecutor(
            address(vault),
            address(sakuraVault),
            address(hyperliquidVault)
        );

        // Setup authorization
        executor.setBackendAuthorization(backend, true);

        // Setup test accounts
        vm.deal(user, 10 ether);
        vm.deal(backend, 1 ether);

        // Configure vaults
        sakuraVault.setMainVault(address(vault));
        vault.setVaultAddresses(address(sakuraVault), address(hyperliquidVault));

        // Mint USDC to user for testing
        usdc.mint(user, 10000e6);
        usdc.mint(address(vault), 10000e6);
    }

    function testExecutorInitialization() public {
        // Check initial state
        assertTrue(executor.authorizedBackends(backend), "Backend should be authorized");
        assertFalse(executor.authorizedBackends(user), "User should not be authorized");

        // Check cooldowns are set
        assertEq(executor.executionCooldown(IFlowAgentVault.AgentType.SAKURA), 1 hours);
        assertEq(executor.executionCooldown(IFlowAgentVault.AgentType.RYU), 5 minutes);
        assertEq(executor.executionCooldown(IFlowAgentVault.AgentType.YUKI), 1 minutes);

        // Check daily limits
        assertEq(executor.maxDailyExecutions(IFlowAgentVault.AgentType.SAKURA), 10);
        assertEq(executor.maxDailyExecutions(IFlowAgentVault.AgentType.RYU), 100);
        assertEq(executor.maxDailyExecutions(IFlowAgentVault.AgentType.YUKI), 200);

        // Check max amounts
        assertEq(executor.maxExecutionAmount(IFlowAgentVault.AgentType.SAKURA), 50000e6);
        assertEq(executor.maxExecutionAmount(IFlowAgentVault.AgentType.RYU), 10000e6);
        assertEq(executor.maxExecutionAmount(IFlowAgentVault.AgentType.YUKI), 5000e6);
    }

    function testExecuteSakuraStrategy() public {
        address pendleMarket = address(0x123);
        uint256 amount = 1000e6; // $1000

        vm.startPrank(backend);

        // Add approved market first
        vm.stopPrank();
        sakuraVault.addApprovedMarket(pendleMarket);
        vm.startPrank(backend);

        // Expect execution events
        vm.expectEmit(true, true, false, true);
        emit AgentExecutionRequested(user, IFlowAgentVault.AgentType.SAKURA, bytes32(0), amount);

        vm.expectEmit(true, true, false, true);
        emit AgentExecutionCompleted(user, IFlowAgentVault.AgentType.SAKURA, 0, true);

        // Execute strategy
        executor.executeSakuraStrategy(user, pendleMarket, amount);

        vm.stopPrank();

        // Check execution record
        AgentExecutor.ExecutionRecord memory record = executor.getExecutionRecord(0);
        assertEq(record.user, user);
        assertEq(uint8(record.agentType), uint8(IFlowAgentVault.AgentType.SAKURA));
        assertEq(record.amount, amount);
        assertTrue(record.success);

        // Check user execution history
        uint256[] memory userExecutions = executor.getUserExecutionHistory(user);
        assertEq(userExecutions.length, 1);
        assertEq(userExecutions[0], 0);
    }

    function testExecuteRyuTrade() public {
        string memory symbol = "ETH/USDC";
        uint256 amount = 500e6; // $500
        uint256 targetPrice = 2500e6; // $2500

        vm.startPrank(backend);

        // Execute spot buy
        executor.executeRyuTrade(
            user,
            symbol,
            IHyperliquidVault.TradeType.SPOT_BUY,
            amount,
            targetPrice
        );

        vm.stopPrank();

        // Check execution was recorded
        uint256[] memory userExecutions = executor.getUserExecutionHistory(user);
        assertEq(userExecutions.length, 1);

        AgentExecutor.ExecutionRecord memory record = executor.getExecutionRecord(userExecutions[0]);
        assertEq(record.user, user);
        assertEq(uint8(record.agentType), uint8(IFlowAgentVault.AgentType.RYU));
        assertEq(record.amount, amount);
    }

    function testExecuteYukiFutures() public {
        string memory symbol = "BTC/USD";
        uint256 amount = 1000e6; // $1000
        uint256 targetPrice = 50000e6; // $50000

        vm.startPrank(backend);

        // Execute futures long
        executor.executeYukiFutures(
            user,
            symbol,
            IHyperliquidVault.TradeType.PERP_LONG,
            amount,
            targetPrice
        );

        vm.stopPrank();

        // Check execution was recorded
        uint256[] memory userExecutions = executor.getUserExecutionHistory(user);
        assertEq(userExecutions.length, 1);

        AgentExecutor.ExecutionRecord memory record = executor.getExecutionRecord(userExecutions[0]);
        assertEq(record.user, user);
        assertEq(uint8(record.agentType), uint8(IFlowAgentVault.AgentType.YUKI));
        assertEq(record.amount, amount);
    }

    function testCooldownEnforcement() public {
        address pendleMarket = address(0x123);
        uint256 amount = 1000e6;

        // Add approved market
        sakuraVault.addApprovedMarket(pendleMarket);

        vm.startPrank(backend);

        // First execution should succeed
        executor.executeSakuraStrategy(user, pendleMarket, amount);

        // Second execution immediately should fail due to cooldown
        vm.expectRevert("Cooldown period not met");
        executor.executeSakuraStrategy(user, pendleMarket, amount);

        vm.stopPrank();

        // Fast forward time past cooldown
        vm.warp(block.timestamp + 1 hours + 1);

        vm.startPrank(backend);

        // Now should work
        executor.executeSakuraStrategy(user, pendleMarket, amount);

        vm.stopPrank();

        // Check two executions recorded
        uint256[] memory userExecutions = executor.getUserExecutionHistory(user);
        assertEq(userExecutions.length, 2);
    }

    function testDailyLimitEnforcement() public {
        string memory symbol = "ETH/USDC";
        uint256 amount = 100e6;
        uint256 targetPrice = 2500e6;

        // Set a low daily limit for testing
        executor.setMaxDailyExecutions(IFlowAgentVault.AgentType.RYU, 2);

        vm.startPrank(backend);

        // First execution
        executor.executeRyuTrade(user, symbol, IHyperliquidVault.TradeType.SPOT_BUY, amount, targetPrice);

        // Fast forward to bypass cooldown
        vm.warp(block.timestamp + 6 minutes);

        // Second execution
        executor.executeRyuTrade(user, symbol, IHyperliquidVault.TradeType.SPOT_BUY, amount, targetPrice);

        // Fast forward to bypass cooldown
        vm.warp(block.timestamp + 6 minutes);

        // Third execution should fail due to daily limit
        vm.expectRevert("Daily execution limit exceeded");
        executor.executeRyuTrade(user, symbol, IHyperliquidVault.TradeType.SPOT_BUY, amount, targetPrice);

        vm.stopPrank();

        // Fast forward to next day
        vm.warp(block.timestamp + 1 days);

        vm.startPrank(backend);

        // Should work on new day
        executor.executeRyuTrade(user, symbol, IHyperliquidVault.TradeType.SPOT_BUY, amount, targetPrice);

        vm.stopPrank();
    }

    function testAmountLimitEnforcement() public {
        address pendleMarket = address(0x123);
        uint256 excessiveAmount = 60000e6; // Above $50k limit for Sakura

        sakuraVault.addApprovedMarket(pendleMarket);

        vm.startPrank(backend);

        vm.expectRevert("Amount exceeds limit");
        executor.executeSakuraStrategy(user, pendleMarket, excessiveAmount);

        vm.stopPrank();
    }

    function testUnauthorizedBackend() public {
        address unauthorized = address(0x999);
        address pendleMarket = address(0x123);
        uint256 amount = 1000e6;

        vm.startPrank(unauthorized);

        vm.expectRevert("Not authorized backend");
        executor.executeSakuraStrategy(user, pendleMarket, amount);

        vm.stopPrank();
    }

    function testCanExecuteView() public {
        // Initially should be able to execute
        assertTrue(executor.canExecute(user, IFlowAgentVault.AgentType.SAKURA));
        assertTrue(executor.canExecute(user, IFlowAgentVault.AgentType.RYU));
        assertTrue(executor.canExecute(user, IFlowAgentVault.AgentType.YUKI));

        // After execution, should be false due to cooldown
        address pendleMarket = address(0x123);
        uint256 amount = 1000e6;

        sakuraVault.addApprovedMarket(pendleMarket);

        vm.prank(backend);
        executor.executeSakuraStrategy(user, pendleMarket, amount);

        // Should not be able to execute Sakura due to cooldown
        assertFalse(executor.canExecute(user, IFlowAgentVault.AgentType.SAKURA));
        // But other agents should still be available
        assertTrue(executor.canExecute(user, IFlowAgentVault.AgentType.RYU));
        assertTrue(executor.canExecute(user, IFlowAgentVault.AgentType.YUKI));
    }

    function testGetTimeUntilNextExecution() public {
        address pendleMarket = address(0x123);
        uint256 amount = 1000e6;

        sakuraVault.addApprovedMarket(pendleMarket);

        // Initially should be 0
        assertEq(executor.getTimeUntilNextExecution(user, IFlowAgentVault.AgentType.SAKURA), 0);

        vm.prank(backend);
        executor.executeSakuraStrategy(user, pendleMarket, amount);

        // Should now show time remaining
        uint256 timeRemaining = executor.getTimeUntilNextExecution(user, IFlowAgentVault.AgentType.SAKURA);
        assertGt(timeRemaining, 0);
        assertLe(timeRemaining, 1 hours);

        // After cooldown passes
        vm.warp(block.timestamp + 1 hours + 1);
        assertEq(executor.getTimeUntilNextExecution(user, IFlowAgentVault.AgentType.SAKURA), 0);
    }

    function testInvalidTradeTypes() public {
        string memory symbol = "ETH/USDC";
        uint256 amount = 500e6;
        uint256 targetPrice = 2500e6;

        vm.startPrank(backend);

        // Ryu should not accept futures trade types
        vm.expectRevert("Invalid trade type for Ryu");
        executor.executeRyuTrade(user, symbol, IHyperliquidVault.TradeType.PERP_LONG, amount, targetPrice);

        // Yuki should not accept spot trade types
        vm.expectRevert("Invalid trade type for Yuki");
        executor.executeYukiFutures(user, symbol, IHyperliquidVault.TradeType.SPOT_BUY, amount, targetPrice);

        vm.stopPrank();
    }

    function testOwnerOnlyFunctions() public {
        vm.startPrank(user);

        vm.expectRevert("Ownable: caller is not the owner");
        executor.setBackendAuthorization(backend, false);

        vm.expectRevert("Ownable: caller is not the owner");
        executor.setCooldown(IFlowAgentVault.AgentType.SAKURA, 2 hours);

        vm.expectRevert("Ownable: caller is not the owner");
        executor.setMaxExecutionAmount(IFlowAgentVault.AgentType.SAKURA, 100000e6);

        vm.stopPrank();
    }

    function testPauseFunctionality() public {
        address pendleMarket = address(0x123);
        uint256 amount = 1000e6;

        sakuraVault.addApprovedMarket(pendleMarket);

        // Pause the executor
        executor.pause();

        vm.startPrank(backend);

        vm.expectRevert("Pausable: paused");
        executor.executeSakuraStrategy(user, pendleMarket, amount);

        vm.stopPrank();

        // Unpause and try again
        executor.unpause();

        vm.prank(backend);
        executor.executeSakuraStrategy(user, pendleMarket, amount);

        // Should succeed after unpause
        uint256[] memory userExecutions = executor.getUserExecutionHistory(user);
        assertEq(userExecutions.length, 1);
    }

    function testEmergencyStopAgent() public {
        // Initially can execute
        assertTrue(executor.canExecute(user, IFlowAgentVault.AgentType.SAKURA));

        // Emergency stop Sakura agent
        executor.emergencyStopAgent(IFlowAgentVault.AgentType.SAKURA);

        // Should not be able to execute anymore
        assertFalse(executor.canExecute(user, IFlowAgentVault.AgentType.SAKURA));

        // Other agents should still work
        assertTrue(executor.canExecute(user, IFlowAgentVault.AgentType.RYU));
    }

    function testCloseSakuraPosition() public {
        uint256 positionId = 1;

        vm.startPrank(backend);

        // Close position should work
        executor.closeSakuraPosition(user, positionId);

        vm.stopPrank();

        // Check execution was recorded
        uint256[] memory userExecutions = executor.getUserExecutionHistory(user);
        assertEq(userExecutions.length, 1);

        AgentExecutor.ExecutionRecord memory record = executor.getExecutionRecord(userExecutions[0]);
        assertEq(record.user, user);
        assertEq(uint8(record.agentType), uint8(IFlowAgentVault.AgentType.SAKURA));
        assertEq(record.amount, 0); // Close position has no amount
    }
}