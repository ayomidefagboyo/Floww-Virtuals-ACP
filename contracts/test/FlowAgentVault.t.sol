// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/FlowAgentVault.sol";
import "../src/SakuraPendleVault.sol";
import "../src/HyperliquidVault.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

// Mock USDC token for testing
contract MockUSDC is ERC20 {
    constructor() ERC20("Mock USDC", "USDC") {
        _mint(msg.sender, 1000000e6); // 1M USDC
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }

    function decimals() public pure override returns (uint8) {
        return 6;
    }
}

// Mock WETH token for testing
contract MockWETH is ERC20 {
    constructor() ERC20("Mock WETH", "WETH") {
        _mint(msg.sender, 1000e18); // 1000 WETH
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }

    receive() external payable {
        _mint(msg.sender, msg.value);
    }
}

// Mock Uniswap V3 Router for testing
contract MockUniswapV3Router {
    MockUSDC public usdc;
    MockWETH public weth;

    constructor(address _usdc, address _weth) {
        usdc = MockUSDC(_usdc);
        weth = MockWETH(_weth);
    }

    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut) {
        // Simple 1 ETH = 2500 USDC mock rate
        if (params.tokenIn == address(weth) && params.tokenOut == address(usdc)) {
            amountOut = params.amountIn * 2500 / 1e18 * 1e6; // Convert to USDC decimals
            usdc.mint(params.recipient, amountOut);
        }

        return amountOut;
    }
}

contract FlowAgentVaultTest is Test {
    FlowAgentVault public vault;
    SakuraPendleVault public sakuraVault;
    HyperliquidVault public hyperliquidVault;
    MockUSDC public usdc;
    MockWETH public weth;
    MockUniswapV3Router public router;

    address public treasury = address(0x1);
    address public user = address(0x2);
    address public backend = address(0x3);

    uint256 constant INITIAL_ETH = 10 ether;
    uint256 constant MIN_DELEGATION = 100e6; // $100
    uint256 constant PLATFORM_FEE = 50; // 0.5%

    event FundsDelegated(address indexed user, IFlowAgentVault.AgentType indexed agentType, uint256 amount);

    function setUp() public {
        // Deploy mock tokens
        usdc = new MockUSDC();
        weth = new MockWETH();
        router = new MockUniswapV3Router(address(usdc), address(weth));

        // Deploy vault contracts
        sakuraVault = new SakuraPendleVault();
        vault = new FlowAgentVault(
            address(usdc),
            address(weth),
            address(router),
            treasury
        );
        hyperliquidVault = new HyperliquidVault(address(vault));

        // Configure vault
        vault.setVaultAddresses(address(sakuraVault), address(hyperliquidVault));
        vault.setPlatformFee(PLATFORM_FEE);
        vault.setMinDelegationAmount(MIN_DELEGATION);

        // Setup test accounts
        vm.deal(user, INITIAL_ETH);
        vm.deal(backend, 1 ether);

        // Configure Sakura vault
        sakuraVault.setMainVault(address(vault));

        // Mint some USDC for testing
        usdc.mint(address(router), 1000000e6);
    }

    function testDepositAndDelegateSakura() public {
        uint256 ethAmount = 1 ether;
        uint256 delegateAmount = 2000e6; // $2000 USDC
        uint256 minUSDCOut = 1900e6; // $1900 minimum (5% slippage)

        vm.startPrank(user);

        // Expect delegation event
        vm.expectEmit(true, true, false, true);
        emit FundsDelegated(user, IFlowAgentVault.AgentType.SAKURA, delegateAmount);

        // Delegate to Sakura
        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.SAKURA,
            delegateAmount,
            minUSDCOut
        );

        vm.stopPrank();

        // Check user balance in Sakura vault
        uint256 userBalance = vault.getUserBalance(user, IFlowAgentVault.AgentType.SAKURA);
        assertGt(userBalance, 0, "User should have balance in Sakura vault");

        // Check gas reserve was maintained
        assertGt(user.balance, 0, "User should have gas reserve remaining");

        // Check treasury received platform fee
        uint256 treasuryBalance = usdc.balanceOf(treasury);
        assertGt(treasuryBalance, 0, "Treasury should receive platform fee");
    }

    function testDepositAndDelegateRyu() public {
        uint256 ethAmount = 2 ether;
        uint256 delegateAmount = 4000e6; // $4000 USDC
        uint256 minUSDCOut = 3800e6; // $3800 minimum

        vm.startPrank(user);

        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.RYU,
            delegateAmount,
            minUSDCOut
        );

        vm.stopPrank();

        // Check user balance in Hyperliquid vault for RYU
        uint256 userBalance = vault.getUserBalance(user, IFlowAgentVault.AgentType.RYU);
        assertGt(userBalance, 0, "User should have balance in RYU vault");
    }

    function testMinDelegationEnforcement() public {
        uint256 ethAmount = 0.1 ether;
        uint256 delegateAmount = 50e6; // $50 USDC (below minimum)
        uint256 minUSDCOut = 45e6;

        vm.startPrank(user);

        // Should revert due to minimum delegation
        vm.expectRevert("Delegation amount too low");
        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.SAKURA,
            delegateAmount,
            minUSDCOut
        );

        vm.stopPrank();
    }

    function testWithdraw() public {
        // First delegate some funds
        uint256 ethAmount = 1 ether;
        uint256 delegateAmount = 2000e6;
        uint256 minUSDCOut = 1900e6;

        vm.startPrank(user);

        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.SAKURA,
            delegateAmount,
            minUSDCOut
        );

        // Check initial balance
        uint256 initialBalance = vault.getUserBalance(user, IFlowAgentVault.AgentType.SAKURA);
        assertGt(initialBalance, 0, "User should have initial balance");

        // Withdraw half
        uint256 withdrawAmount = initialBalance / 2;
        vault.withdraw(IFlowAgentVault.AgentType.SAKURA, withdrawAmount);

        // Check balance reduced
        uint256 finalBalance = vault.getUserBalance(user, IFlowAgentVault.AgentType.SAKURA);
        assertEq(finalBalance, initialBalance - withdrawAmount, "Balance should be reduced by withdrawal amount");

        vm.stopPrank();
    }

    function testWithdrawAll() public {
        // First delegate some funds
        uint256 ethAmount = 1 ether;
        uint256 delegateAmount = 2000e6;
        uint256 minUSDCOut = 1900e6;

        vm.startPrank(user);

        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.SAKURA,
            delegateAmount,
            minUSDCOut
        );

        // Withdraw all
        vault.withdrawAll(IFlowAgentVault.AgentType.SAKURA);

        // Check balance is zero
        uint256 finalBalance = vault.getUserBalance(user, IFlowAgentVault.AgentType.SAKURA);
        assertEq(finalBalance, 0, "Balance should be zero after withdrawing all");

        vm.stopPrank();
    }

    function testGasReserveMaintained() public {
        uint256 ethAmount = 1 ether;
        uint256 delegateAmount = 2000e6;
        uint256 minUSDCOut = 1900e6;
        uint256 initialBalance = user.balance;

        vm.startPrank(user);

        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.SAKURA,
            delegateAmount,
            minUSDCOut
        );

        vm.stopPrank();

        // Check that some ETH remains for gas
        uint256 finalBalance = user.balance;
        assertLt(finalBalance, initialBalance, "ETH should be consumed");
        assertGt(finalBalance, 0.05 ether, "Gas reserve should be maintained");
    }

    function testPlatformFeeCollection() public {
        uint256 ethAmount = 1 ether;
        uint256 delegateAmount = 2000e6;
        uint256 minUSDCOut = 1900e6;
        uint256 initialTreasuryBalance = usdc.balanceOf(treasury);

        vm.startPrank(user);

        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.SAKURA,
            delegateAmount,
            minUSDCOut
        );

        vm.stopPrank();

        // Check treasury received fee
        uint256 finalTreasuryBalance = usdc.balanceOf(treasury);
        assertGt(finalTreasuryBalance, initialTreasuryBalance, "Treasury should receive platform fee");

        // Fee should be approximately 0.5% of delegation amount
        uint256 expectedFee = (delegateAmount * PLATFORM_FEE) / 10000;
        uint256 actualFee = finalTreasuryBalance - initialTreasuryBalance;

        // Allow for some variance due to ETH->USDC conversion
        assertApproxEqRel(actualFee, expectedFee, 0.1e18, "Platform fee should be approximately correct");
    }

    function testInsufficientETH() public {
        uint256 ethAmount = 0.01 ether; // Very small amount
        uint256 delegateAmount = 2000e6; // $2000 USDC (impossible with 0.01 ETH)
        uint256 minUSDCOut = 1900e6;

        vm.startPrank(user);

        // Should revert due to insufficient ETH
        vm.expectRevert();
        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.SAKURA,
            delegateAmount,
            minUSDCOut
        );

        vm.stopPrank();
    }

    function testOnlyOwnerFunctions() public {
        // Test that non-owner cannot call owner-only functions
        vm.startPrank(user);

        vm.expectRevert("Ownable: caller is not the owner");
        vault.setPlatformFee(100);

        vm.expectRevert("Ownable: caller is not the owner");
        vault.setMinDelegationAmount(200e6);

        vm.expectRevert("Ownable: caller is not the owner");
        vault.setVaultAddresses(address(sakuraVault), address(hyperliquidVault));

        vm.stopPrank();
    }

    function testPauseUnpause() public {
        // Test pause functionality
        vault.pause();

        vm.startPrank(user);

        vm.expectRevert("Pausable: paused");
        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.SAKURA,
            2000e6,
            1900e6
        );

        vm.stopPrank();

        // Test unpause
        vault.unpause();

        vm.startPrank(user);

        // Should work after unpause
        vault.depositAndDelegate{value: 1 ether}(
            IFlowAgentVault.AgentType.SAKURA,
            2000e6,
            1900e6
        );

        vm.stopPrank();
    }

    // Test helper functions
    function testGetUserBalances() public {
        uint256 ethAmount = 1 ether;
        uint256 delegateAmount = 2000e6;
        uint256 minUSDCOut = 1900e6;

        vm.startPrank(user);

        // Delegate to Sakura
        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.SAKURA,
            delegateAmount,
            minUSDCOut
        );

        // Delegate to RYU
        vault.depositAndDelegate{value: ethAmount}(
            IFlowAgentVault.AgentType.RYU,
            delegateAmount,
            minUSDCOut
        );

        vm.stopPrank();

        // Check balances
        uint256 sakuraBalance = vault.getUserBalance(user, IFlowAgentVault.AgentType.SAKURA);
        uint256 ryuBalance = vault.getUserBalance(user, IFlowAgentVault.AgentType.RYU);

        assertGt(sakuraBalance, 0, "Sakura balance should be greater than zero");
        assertGt(ryuBalance, 0, "RYU balance should be greater than zero");
    }

    receive() external payable {}
}