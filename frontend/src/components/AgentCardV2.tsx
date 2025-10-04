'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  TrendingUp,
  DollarSign,
  Shield,
  Zap,
  Leaf,
  ArrowRight,
  Loader2,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { Agent } from '@/types/agents_v2';

interface AgentCardV2Props {
  agent: Agent;
  onAction?: (agentId: string, data?: any) => Promise<void>;
  isLoading?: boolean;
  lastResult?: {
    success: boolean;
    timestamp: string;
    summary?: string;
  };
}

const getAgentIcon = (agentId: string) => {
  switch (agentId) {
    case 'ryu':
      return <Search className="w-6 h-6" />;
    case 'yuki':
      return <Zap className="w-6 h-6" />;
    case 'sakura':
      return <Leaf className="w-6 h-6" />;
    default:
      return <Shield className="w-6 h-6" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'online':
      return 'text-green-400';
    case 'analyzing':
      return 'text-yellow-400';
    case 'offline':
      return 'text-red-400';
    case 'error':
      return 'text-red-500';
    default:
      return 'text-gray-400';
  }
};

const getStatusDot = (status: string) => {
  const baseClass = 'w-2 h-2 rounded-full';
  switch (status) {
    case 'online':
      return `${baseClass} bg-green-400 animate-pulse-soft`;
    case 'analyzing':
      return `${baseClass} bg-yellow-400 animate-pulse`;
    case 'offline':
      return `${baseClass} bg-red-400`;
    case 'error':
      return `${baseClass} bg-red-500 animate-pulse`;
    default:
      return `${baseClass} bg-gray-400`;
  }
};

const getRiskLevelColor = (riskLevel: string) => {
  switch (riskLevel.toLowerCase()) {
    case 'low':
      return 'text-green-400 bg-green-400/10';
    case 'medium':
      return 'text-yellow-400 bg-yellow-400/10';
    case 'high':
      return 'text-red-400 bg-red-400/10';
    default:
      return 'text-gray-400 bg-gray-400/10';
  }
};

export default function AgentCardV2({ agent, onAction, isLoading, lastResult }: AgentCardV2Props) {
  const [tokenInput, setTokenInput] = useState('');
  const [investmentAmount, setInvestmentAmount] = useState('10000');
  const [inputError, setInputError] = useState('');

  const handleAction = async () => {
    if (agent.id === 'ryu') {
      // Token analysis requires input
      if (!tokenInput.trim()) {
        setInputError('Please enter a token symbol');
        return;
      }
      setInputError('');
    }

    if (agent.id === 'sakura') {
      // Validate investment amount
      const amount = parseFloat(investmentAmount);
      if (isNaN(amount) || amount <= 0) {
        setInputError('Please enter a valid investment amount');
        return;
      }
      setInputError('');
    }

    try {
      let data;
      if (agent.id === 'ryu') {
        data = { symbol: tokenInput.toUpperCase() };
      } else if (agent.id === 'sakura') {
        data = { investment_amount: parseFloat(investmentAmount) };
      }
      await onAction?.(agent.id, data);
    } catch (error) {
      console.error('Action failed:', error);
    }
  };

  const handleInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isLoading) {
      handleAction();
    }
  };

  const isDisabled = isLoading || ['offline', 'error'].includes(agent.status);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3 }}
      className="bg-gray-900/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 hover:border-blue-500/50 transition-all duration-300 group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-4">
          {/* Icon */}
          <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400 group-hover:bg-blue-500/20 transition-colors">
            {getAgentIcon(agent.id)}
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white mb-1">
              {agent.name}
            </h3>
            <p className="text-sm text-gray-400 leading-relaxed max-w-xs">
              {agent.description}
            </p>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center gap-2">
          <div className={getStatusDot(agent.status)} />
          <span className={`text-xs font-medium capitalize ${getStatusColor(agent.status)}`}>
            {agent.status}
          </span>
        </div>
      </div>

      {/* Specialty Badge */}
      <div className="mb-6">
        <div className="inline-flex items-center px-3 py-1 rounded-full bg-gray-700/50 text-gray-300 text-xs font-medium">
          {agent.specialty}
        </div>
      </div>

      {/* Last Result */}
      {lastResult && (
        <div className="mb-4 p-3 rounded-lg bg-gray-800/30 border border-gray-700/30">
          <div className="flex items-center gap-2 mb-1">
            {lastResult.success ? (
              <CheckCircle className="w-4 h-4 text-green-400" />
            ) : (
              <XCircle className="w-4 h-4 text-red-400" />
            )}
            <span className="text-sm font-medium text-gray-300">
              Last Analysis
            </span>
            <span className="text-xs text-gray-500 ml-auto">
              {new Date(lastResult.timestamp).toLocaleTimeString()}
            </span>
          </div>
          {lastResult.summary && (
            <p className="text-xs text-gray-400">
              {lastResult.summary}
            </p>
          )}
        </div>
      )}

      {/* Input Section (Ryu & Sakura Agents) */}
      <AnimatePresence>
        {agent.id === 'ryu' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6"
          >
            <label className="block text-sm text-gray-400 mb-2">
              Token Symbol
            </label>
            <div className="relative">
              <input
                type="text"
                value={tokenInput}
                onChange={(e) => {
                  setTokenInput(e.target.value);
                  setInputError('');
                }}
                onKeyPress={handleInputKeyPress}
                placeholder="e.g., BTC, ETH, DOGE"
                className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                disabled={isDisabled}
              />
              {inputError && (
                <div className="flex items-center gap-1 mt-1 text-xs text-red-400">
                  <AlertCircle className="w-3 h-3" />
                  {inputError}
                </div>
              )}
            </div>
          </motion.div>
        )}
        {agent.id === 'sakura' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6"
          >
            <label className="block text-sm text-gray-400 mb-2">
              Investment Amount (USD)
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <DollarSign className="h-4 w-4 text-gray-500" />
              </div>
              <input
                type="number"
                value={investmentAmount}
                onChange={(e) => {
                  setInvestmentAmount(e.target.value);
                  setInputError('');
                }}
                onKeyPress={handleInputKeyPress}
                placeholder="10000"
                min="1"
                step="100"
                className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                disabled={isDisabled}
              />
              {inputError && (
                <div className="flex items-center gap-1 mt-1 text-xs text-red-400">
                  <AlertCircle className="w-3 h-3" />
                  {inputError}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Expected Results Preview */}
      <div className="mb-6 p-4 rounded-lg bg-gray-800/30 border border-gray-700/30">
        <h4 className="text-sm font-medium text-gray-200 mb-2">
          {agent.resultType}
        </h4>
        <div className="text-xs text-gray-400 space-y-1">
          {agent.id === 'ryu' && (
            <>
              <div>• Complete token analysis with confidence scoring</div>
              <div>• Entry/exit levels with risk management</div>
              <div>• Technical indicators and market insights</div>
            </>
          )}
          {agent.id === 'yuki' && (
            <>
              <div>• Real-time market scanning across top pairs</div>
              <div>• High-confidence trade opportunities</div>
              <div>• Precise entry/target levels with timing</div>
            </>
          )}
          {agent.id === 'sakura' && (
            <>
              <div>• Conservative DeFi yield farming options</div>
              <div>• Personalized returns based on investment</div>
              <div>• Portfolio allocation with dollar amounts</div>
            </>
          )}
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={handleAction}
        disabled={isDisabled}
        className={`
          w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2
          ${
            isDisabled
              ? 'bg-gray-700/50 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-500 text-white hover:shadow-lg hover:shadow-blue-500/25 group'
          }
        `}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>
              {agent.id === 'ryu' && 'Analyzing Token...'}
              {agent.id === 'yuki' && 'Scanning Markets...'}
              {agent.id === 'sakura' && 'Finding Yields...'}
            </span>
          </>
        ) : (
          <>
            <span>{agent.actionLabel}</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </>
        )}
      </button>

      {/* Status Message */}
      {agent.status === 'offline' && (
        <div className="mt-3 text-center text-xs text-red-400">
          Agent is currently offline
        </div>
      )}
      {agent.status === 'error' && (
        <div className="mt-3 text-center text-xs text-red-400">
          Agent encountered an error
        </div>
      )}
    </motion.div>
  );
}