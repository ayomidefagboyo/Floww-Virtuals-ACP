#!/bin/bash

# Flow AI Agent Delegation System Test Runner
# Usage: ./test.sh [options]

set -e

SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Flow AI Agent Test Suite${NC}"
echo ""

# Check if foundry is installed
if ! command -v forge &> /dev/null; then
    echo -e "${RED}❌ Foundry not found${NC}"
    echo "Install Foundry: curl -L https://foundry.paradigm.xyz | bash && foundryup"
    exit 1
fi

# Parse command line options
VERBOSE=false
GAS_REPORT=false
COVERAGE=false
SPECIFIC_TEST=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -g|--gas)
            GAS_REPORT=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -t|--test)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./test.sh [options]"
            echo "Options:"
            echo "  -v, --verbose    Verbose output"
            echo "  -g, --gas        Generate gas report"
            echo "  -c, --coverage   Generate coverage report"
            echo "  -t, --test NAME  Run specific test"
            echo "  -h, --help       Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Build contracts first
echo -e "${YELLOW}🔨 Building contracts...${NC}"
forge build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful${NC}"
echo ""

# Prepare test command
TEST_CMD="forge test"

if [ "$VERBOSE" = true ]; then
    TEST_CMD="$TEST_CMD -vvv"
fi

if [ "$GAS_REPORT" = true ]; then
    TEST_CMD="$TEST_CMD --gas-report"
fi

if [ "$COVERAGE" = true ]; then
    # Generate coverage report
    echo -e "${YELLOW}📊 Generating coverage report...${NC}"
    forge coverage --report lcov

    # Install lcov if not present (for detailed HTML reports)
    if command -v genhtml &> /dev/null; then
        genhtml -o coverage_report lcov.info
        echo -e "${GREEN}📊 Coverage HTML report generated in coverage_report/${NC}"
    else
        echo -e "${YELLOW}⚠️  Install lcov for HTML coverage reports: brew install lcov${NC}"
    fi
fi

if [ -n "$SPECIFIC_TEST" ]; then
    TEST_CMD="$TEST_CMD --match-test $SPECIFIC_TEST"
fi

# Run tests
echo -e "${YELLOW}🧪 Running tests...${NC}"
echo "Command: $TEST_CMD"
echo ""

$TEST_CMD

TEST_EXIT_CODE=$?

echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"

    # Show test summary
    echo -e "${BLUE}📋 Test Summary:${NC}"

    # Count test files
    TEST_FILES=$(find test -name "*.t.sol" | wc -l)
    echo "  Test files: $TEST_FILES"

    # Count test functions (approximate)
    TEST_FUNCTIONS=$(grep -r "function test" test/ | wc -l)
    echo "  Test functions: ~$TEST_FUNCTIONS"

    if [ "$GAS_REPORT" = true ]; then
        echo ""
        echo -e "${BLUE}⛽ Gas usage report generated above${NC}"
    fi

    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${BLUE}📊 Coverage report:${NC}"
        forge coverage --report summary
    fi

else
    echo -e "${RED}❌ Tests failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🎯 Next steps:${NC}"
echo "  1. Review test coverage and add more tests if needed"
echo "  2. Check gas usage and optimize if necessary"
echo "  3. Run tests on different scenarios and edge cases"
echo "  4. Consider fuzzing tests for better coverage"

echo ""
echo -e "${GREEN}🎉 Test suite complete!${NC}"