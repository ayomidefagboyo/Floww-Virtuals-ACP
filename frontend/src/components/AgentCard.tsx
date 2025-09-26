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
  AlertCircle
} from 'lucide-react';
import { Agent } from '@/types/agents';

interface AgentCardProps {
  agent: Agent;
  onAction?: (agentId: string, data?: any) => Promise<void>;
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
      return 'text-success-400';
    case 'analyzing':
      return 'text-warning-400';
    case 'offline':
      return 'text-error-400';
    default:
      return 'text-primary-400';
  }
};

const getStatusDot = (status: string) => {
  const baseClass = 'w-2 h-2 rounded-full';
  switch (status) {
    case 'online':
      return `${baseClass} bg-success-400 animate-pulse-soft`;
    case 'analyzing':
      return `${baseClass} bg-warning-400 animate-pulse`;
    case 'offline':
      return `${baseClass} bg-error-400`;
    default:
      return `${baseClass} bg-primary-400`;
  }
};

export default function AgentCard({ agent, onAction }: AgentCardProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [tokenInput, setTokenInput] = useState('');
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

    setIsProcessing(true);
    try {
      const data = agent.id === 'ryu' ? { symbol: tokenInput.toUpperCase() } : undefined;
      await onAction?.(agent.id, data);
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAction();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3 }}
      className="card-premium group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-4">
          {/* Icon - hidden on mobile for more compact view */}
          <div className="hidden sm:block p-3 rounded-xl bg-accent-500/10 text-accent-400 group-hover:bg-accent-500/20 transition-colors">
            {getAgentIcon(agent.id)}
          </div>
          <div>
            <h3 className="text-xl font-semibold text-primary-100 mb-1">
              {agent.name}
            </h3>
            <p className="text-sm text-primary-400 leading-relaxed">
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
        <div className="inline-flex items-center px-3 py-1 rounded-full bg-primary-700/50 text-primary-300 text-xs font-medium">
          {agent.specialty}
        </div>
      </div>

      {/* Input Section (Ryu Agent Only) */}
      <AnimatePresence>
        {agent.id === 'ryu' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6"
          >
            <label className="block text-sm text-primary-400 mb-2">
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
                className="w-full bg-primary-800/50 border border-primary-700/50 rounded-lg px-4 py-2 text-primary-100 placeholder-primary-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent transition-colors"
                disabled={isProcessing}
              />
              {inputError && (
                <div className="flex items-center gap-1 mt-1 text-xs text-error-400">
                  <AlertCircle className="w-3 h-3" />
                  {inputError}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Expected Results Preview */}
      <div className="mb-6 p-4 rounded-lg bg-primary-800/30 border border-primary-700/30">
        <h4 className="text-sm font-medium text-primary-200 mb-2">
          {agent.resultType}
        </h4>
        <div className="text-xs text-primary-400 space-y-1">
          {agent.id === 'ryu' && (
            <>
              <div>• Complete token analysis with AI scoring</div>
              <div>• Entry/exit levels with risk management</div>
              <div>• Technical, fundamental & sentiment insights</div>
            </>
          )}
          {agent.id === 'yuki' && (
            <>
              <div>• Real-time market scanning across 500+ pairs</div>
              <div>• High-confidence trade opportunities</div>
              <div>• Precise entry/target levels with timing</div>
            </>
          )}
          {agent.id === 'sakura' && (
            <>
              <div>• Conservative DeFi yield farming options</div>
              <div>• Risk-adjusted APY projections</div>
              <div>• Portfolio allocation recommendations</div>
            </>
          )}
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={handleAction}
        disabled={isProcessing || agent.status === 'offline'}
        className={`
          w-full py-3 px-4 rounded-lg font-medium transition-all duration-200
          ${
            isProcessing || agent.status === 'offline'
              ? 'bg-primary-700/50 text-primary-500 cursor-not-allowed'
              : 'btn-primary group'
          }
        `}
      >
        <div className="flex items-center justify-center gap-2">
          {isProcessing ? (
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
        </div>
      </button>

      {/* Status Message */}
      {agent.status === 'offline' && (
        <div className="mt-3 text-center text-xs text-error-400">
          Agent is currently offline
        </div>
      )}
    </motion.div>
  );
}