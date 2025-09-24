// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title VirtualsACP
 * @notice Flow AI agents integration with Virtuals Agent Commerce Protocol
 * @dev Implements ACP for onchain agent commerce on Virtuals platform
 */
contract VirtualsACP is ReentrancyGuard, Ownable, Pausable {

    // ACP Phases
    enum ACPPhase {
        Request,
        Negotiation,
        Transaction,
        Evaluation
    }

    // Agent Types
    enum AgentType {
        YUKI,    // Aggressive futures trading
        SAKURA,  // Conservative yield farming
        RYU      // Balanced spot trading
    }

    // Request structure for ACP
    struct AgentRequest {
        bytes32 requestId;
        address requester;
        AgentType agentType;
        string serviceType; // 'analyze' or 'execute'
        uint256 paymentAmount;
        string paymentCurrency;
        bytes32 parametersHash;
        uint256 timestamp;
        ACPPhase phase;
    }

    // Proof of Agreement (PoA)
    struct ProofOfAgreement {
        bytes32 requestId;
        address agentProvider;
        address requester;
        string serviceDescription;
        uint256 agreedPrice;
        string priceCurrency;
        uint256 deliveryTimeframe;
        bytes32 termsHash;
        bool isSigned;
        uint256 timestamp;
    }

    // Transaction record
    struct ACPTransaction {
        bytes32 requestId;
        address requester;
        address agentProvider;
        uint256 paymentAmount;
        string paymentCurrency;
        uint256 serviceValue;
        bool paymentReleased;
        bool serviceDelivered;
        uint256 completionTimestamp;
    }

    // Storage
    mapping(bytes32 => AgentRequest) public requests;
    mapping(bytes32 => ProofOfAgreement) public agreements;
    mapping(bytes32 => ACPTransaction) public transactions;
    mapping(AgentType => string) public agentDescriptions;
    mapping(AgentType => uint256) public agentPricing;
    mapping(AgentType => bool) public agentActive;

    // Events
    event AgentRequestCreated(
        bytes32 indexed requestId,
        address indexed requester,
        AgentType agentType,
        string serviceType,
        uint256 paymentAmount
    );

    event ProofOfAgreementSigned(
        bytes32 indexed requestId,
        address indexed agentProvider,
        uint256 agreedPrice,
        uint256 deliveryTimeframe
    );

    event TransactionInitiated(
        bytes32 indexed requestId,
        address indexed requester,
        address indexed agentProvider,
        uint256 paymentAmount
    );

    event ServiceDelivered(
        bytes32 indexed requestId,
        bool success,
        string result
    );

    event EvaluationCompleted(
        bytes32 indexed requestId,
        uint8 qualityScore,
        bool termsMet
    );

    constructor() {
        // Initialize agent capabilities
        agentDescriptions[AgentType.YUKI] = "Aggressive futures trading with high-risk, high-reward strategies";
        agentDescriptions[AgentType.SAKURA] = "Conservative yield farming and DeFi strategies";
        agentDescriptions[AgentType.RYU] = "Balanced spot trading with AI-powered analysis";

        // Initialize pricing (in wei)
        agentPricing[AgentType.YUKI] = 0.001 ether;    // 0.001 ETH
        agentPricing[AgentType.SAKURA] = 0.0005 ether; // 0.0005 ETH
        agentPricing[AgentType.RYU] = 0.0005 ether;    // 0.0005 ETH

        // Activate all agents
        agentActive[AgentType.YUKI] = true;
        agentActive[AgentType.SAKURA] = true;
        agentActive[AgentType.RYU] = true;
    }

    /**
     * @notice Create a new agent request (ACP Phase 1: Request)
     * @param agentType The type of agent requested
     * @param serviceType Type of service ('analyze' or 'execute')
     * @param parametersHash Hash of service parameters
     */
    function createAgentRequest(
        AgentType agentType,
        string memory serviceType,
        bytes32 parametersHash
    ) external payable nonReentrant whenNotPaused returns (bytes32) {
        require(agentActive[agentType], "Agent not active");
        require(msg.value >= agentPricing[agentType], "Insufficient payment");

        bytes32 requestId = keccak256(abi.encodePacked(
            msg.sender,
            agentType,
            serviceType,
            block.timestamp,
            block.number
        ));

        requests[requestId] = AgentRequest({
            requestId: requestId,
            requester: msg.sender,
            agentType: agentType,
            serviceType: serviceType,
            paymentAmount: msg.value,
            paymentCurrency: "ETH",
            parametersHash: parametersHash,
            timestamp: block.timestamp,
            phase: ACPPhase.Request
        });

        emit AgentRequestCreated(
            requestId,
            msg.sender,
            agentType,
            serviceType,
            msg.value
        );

        return requestId;
    }

    /**
     * @notice Sign Proof of Agreement (ACP Phase 2: Negotiation)
     * @param requestId The request to create agreement for
     * @param serviceDescription Description of the service to be provided
     * @param deliveryTimeframe Timeframe for service delivery (in seconds)
     * @param termsHash Hash of the agreed terms
     */
    function signProofOfAgreement(
        bytes32 requestId,
        string memory serviceDescription,
        uint256 deliveryTimeframe,
        bytes32 termsHash
    ) external onlyOwner nonReentrant {
        require(requests[requestId].phase == ACPPhase.Request, "Invalid phase");
        require(requests[requestId].requester != address(0), "Request not found");

        agreements[requestId] = ProofOfAgreement({
            requestId: requestId,
            agentProvider: msg.sender,
            requester: requests[requestId].requester,
            serviceDescription: serviceDescription,
            agreedPrice: requests[requestId].paymentAmount,
            priceCurrency: requests[requestId].paymentCurrency,
            deliveryTimeframe: deliveryTimeframe,
            termsHash: termsHash,
            isSigned: true,
            timestamp: block.timestamp
        });

        requests[requestId].phase = ACPPhase.Negotiation;

        emit ProofOfAgreementSigned(
            requestId,
            msg.sender,
            requests[requestId].paymentAmount,
            deliveryTimeframe
        );
    }

    /**
     * @notice Initiate transaction (ACP Phase 3: Transaction)
     * @param requestId The request to initiate transaction for
     */
    function initiateTransaction(bytes32 requestId) external onlyOwner nonReentrant {
        require(requests[requestId].phase == ACPPhase.Negotiation, "Invalid phase");
        require(agreements[requestId].isSigned, "Agreement not signed");

        transactions[requestId] = ACPTransaction({
            requestId: requestId,
            requester: requests[requestId].requester,
            agentProvider: msg.sender,
            paymentAmount: requests[requestId].paymentAmount,
            paymentCurrency: requests[requestId].paymentCurrency,
            serviceValue: agreements[requestId].agreedPrice,
            paymentReleased: false,
            serviceDelivered: false,
            completionTimestamp: 0
        });

        requests[requestId].phase = ACPPhase.Transaction;

        emit TransactionInitiated(
            requestId,
            requests[requestId].requester,
            msg.sender,
            requests[requestId].paymentAmount
        );
    }

    /**
     * @notice Deliver service and release payment (ACP Phase 3: Transaction)
     * @param requestId The request to deliver service for
     * @param success Whether the service was delivered successfully
     * @param result The result of the service
     */
    function deliverService(
        bytes32 requestId,
        bool success,
        string memory result
    ) external onlyOwner nonReentrant {
        require(requests[requestId].phase == ACPPhase.Transaction, "Invalid phase");
        require(!transactions[requestId].serviceDelivered, "Already delivered");

        transactions[requestId].serviceDelivered = true;
        transactions[requestId].completionTimestamp = block.timestamp;

        if (success) {
            // Release payment to agent provider
            transactions[requestId].paymentReleased = true;
            payable(owner()).transfer(transactions[requestId].paymentAmount);
        }

        emit ServiceDelivered(requestId, success, result);

        // Move to evaluation phase
        requests[requestId].phase = ACPPhase.Evaluation;
    }

    /**
     * @notice Complete evaluation (ACP Phase 4: Evaluation)
     * @param requestId The request to evaluate
     * @param qualityScore Quality score (1-10)
     * @param termsMet Whether the agreed terms were met
     * @param feedback Evaluation feedback
     */
    function completeEvaluation(
        bytes32 requestId,
        uint8 qualityScore,
        bool termsMet,
        string memory feedback
    ) external {
        require(requests[requestId].phase == ACPPhase.Evaluation, "Invalid phase");
        require(msg.sender == requests[requestId].requester, "Only requester can evaluate");
        require(qualityScore >= 1 && qualityScore <= 10, "Invalid quality score");

        emit EvaluationCompleted(requestId, qualityScore, termsMet);
    }

    /**
     * @notice Get request details
     * @param requestId The request ID to query
     */
    function getRequest(bytes32 requestId) external view returns (AgentRequest memory) {
        return requests[requestId];
    }

    /**
     * @notice Get agreement details
     * @param requestId The request ID to query
     */
    function getAgreement(bytes32 requestId) external view returns (ProofOfAgreement memory) {
        return agreements[requestId];
    }

    /**
     * @notice Get transaction details
     * @param requestId The request ID to query
     */
    function getTransaction(bytes32 requestId) external view returns (ACPTransaction memory) {
        return transactions[requestId];
    }

    /**
     * @notice Emergency functions
     */
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