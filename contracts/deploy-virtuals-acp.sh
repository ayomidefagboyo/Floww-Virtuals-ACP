#!/bin/bash

# Virtuals ACP Contract Deployment Script
# Deploys VirtualsACP.sol to Base networks

set -e

echo "🚀 Deploying VirtualsACP Contract to Base Networks"
echo "=================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one based on .env.example"
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
if [ -z "$PRIVATE_KEY" ]; then
    echo "❌ PRIVATE_KEY not set in .env"
    exit 1
fi

if [ -z "$ALCHEMY_API_KEY" ]; then
    echo "❌ ALCHEMY_API_KEY not set in .env"
    exit 1
fi

if [ -z "$BASESCAN_API_KEY" ]; then
    echo "❌ BASESCAN_API_KEY not set in .env"
    exit 1
fi

echo "✅ Environment variables loaded"

# Get deployer address
DEPLOYER_ADDRESS=$(cast wallet address --private-key $PRIVATE_KEY)
echo "📝 Deployer address: $DEPLOYER_ADDRESS"

# Check if we should deploy to testnet first
if [ "${SKIP_TESTNET:-false}" != "true" ]; then
    echo ""
    echo "🧪 Testing deployment on Base Sepolia (testnet)..."
    echo "🌐 Deploying to Base_Sepolia..."
    echo "RPC URL: https://base-sepolia.g.alchemy.com/v2/$ALCHEMY_API_KEY"
    echo "Chain ID: 84532"
    echo ""
    echo "📦 Deploying VirtualsACP contract..."

    # Deploy to Base Sepolia
    forge script script/DeployVirtualsACP.s.sol:DeployVirtualsACP \
        --rpc-url base_sepolia \
        --private-key $PRIVATE_KEY \
        --broadcast \
        --etherscan-api-key $BASESCAN_API_KEY \
        --verify

    echo ""
    echo "✅ Base Sepolia deployment completed!"
    echo ""
    read -p "Deploy to Base Mainnet? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment stopped. Testnet deployment successful."
        exit 0
    fi
fi

echo ""
echo "🚀 Deploying to Base Mainnet..."
echo "🌐 Deploying to Base_Mainnet..."
echo "RPC URL: https://base-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY"
echo "Chain ID: 8453"
echo ""
echo "📦 Deploying VirtualsACP contract..."

# Deploy to Base Mainnet
forge script script/DeployVirtualsACP.s.sol:DeployVirtualsACP \
    --rpc-url base_mainnet \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --etherscan-api-key $BASESCAN_API_KEY \
    --verify

echo ""
echo "🎉 Deployment completed successfully!"
echo "📋 Check the deployments/ folder for contract addresses"
echo "🔍 Verify on BaseScan:"
echo "   - Testnet: https://sepolia.basescan.org/"
echo "   - Mainnet: https://basescan.org/"