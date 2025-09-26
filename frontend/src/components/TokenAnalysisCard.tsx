'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronRight,
  Loader2,
  AlertCircle,
  Shield,
  Target,
  DollarSign,
  BarChart3,
  Activity,
  Brain
} from 'lucide-react';
import { EnhancedTokenAnalysisRequest, EnhancedTokenAnalysisResponse } from '@/types/agents';

interface TokenAnalysisCardProps {
  onAnalysisComplete?: (result: EnhancedTokenAnalysisResponse) => void;
}

const agentConfig = {
  ryu: {
    name: 'Ryu',
    description: 'Balanced technical & fundamental analysis',
    color: '#3B82F6',
    icon: Shield
  },
  yuki: {
    name: 'Yuki',
    description: 'Aggressive momentum & scalping focus',
    color: '#F59E0B',
    icon: TrendingUp
  },
  sakura: {
    name: 'Sakura',
    description: 'Conservative long-term value investing',
    color: '#EC4899',
    icon: Target
  }
};

const getRecommendationIcon = (recommendation: string) => {
  switch (recommendation) {
    case 'BUY':
      return <TrendingUp className="w-4 h-4" />;
    case 'SELL':
      return <TrendingDown className="w-4 h-4" />;
    case 'HOLD':
    default:
      return <Minus className="w-4 h-4" />;
  }
};

const getRecommendationColor = (recommendation: string) => {
  switch (recommendation) {
    case 'BUY':
      return 'text-green-500';
    case 'SELL':
      return 'text-red-500';
    case 'HOLD':
    default:
      return 'text-amber-500';
  }
};

const getAnalysisScoreColor = (score: number) => {
  if (score >= 0.7) return 'text-green-500';
  if (score >= 0.4) return 'text-amber-500';
  return 'text-red-500';
};

const SimpleTokenImage = ({ symbol, imageUrl, size = 'md' }: {
  symbol: string;
  imageUrl?: string;
  size?: 'sm' | 'md' | 'lg';
}) => {
  const sizeClass = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }[size];

  return (
    <div className={`${sizeClass} rounded-full bg-primary-700 flex items-center justify-center overflow-hidden`}>
      {imageUrl ? (
        <img src={imageUrl} alt={symbol} className="w-full h-full object-cover" />
      ) : (
        <span className="text-primary-200 font-semibold text-xs">
          {symbol.slice(0, 2)}
        </span>
      )}
    </div>
  );
};

const AnimeMascot = ({
  mood,
  message,
  agentColor,
  className
}: {
  mood: 'neutral' | 'excited' | 'analyzing';
  message: string;
  agentColor: string;
  className?: string;
}) => {
  return (
    <div className={`flex flex-col items-center ${className}`}>
      <motion.div
        animate={{
          scale: mood === 'analyzing' ? [1, 1.1, 1] : 1,
          rotate: mood === 'excited' ? [0, 5, -5, 0] : 0
        }}
        transition={{
          duration: mood === 'analyzing' ? 1.5 : 2,
          repeat: mood === 'analyzing' ? Infinity : 3,
          ease: 'easeInOut'
        }}
        className="w-16 h-16 rounded-full flex items-center justify-center mb-2"
        style={{ backgroundColor: `${agentColor}20`, border: `2px solid ${agentColor}` }}
      >
        <Brain className="w-8 h-8" style={{ color: agentColor }} />
      </motion.div>
      <p className="text-sm text-primary-300 text-center">{message}</p>
    </div>
  );
};

export default function TokenAnalysisCard({ onAnalysisComplete }: TokenAnalysisCardProps) {
  const [tokenTicker, setTokenTicker] = useState('');
  const [agentType, setAgentType] = useState<'ryu' | 'yuki' | 'sakura'>('ryu');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<EnhancedTokenAnalysisResponse | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [showAnalysisInput, setShowAnalysisInput] = useState(true);
  const [isAIInsightsModalOpen, setIsAIInsightsModalOpen] = useState(false);

  const handleAnalyzeToken = async () => {
    // 1. Validate input
    if (!tokenTicker.trim()) {
      setAnalysisError('Please enter a token ticker (e.g., BTC, ETH, SOL)');
      return;
    }

    // 2. Proceed to analysis
    await performTokenAnalysis();
  };

  const performTokenAnalysis = async () => {
    setIsAnalyzing(true);
    setAnalysisError(null);
    setAnalysisResult(null);

    try {
      // Make token analysis API call
      const response = await fetch('/api/token-analysis/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token_ticker: tokenTicker.toUpperCase(),
          agent_type: agentType,
          include_sentiment: true,
          include_technical: true,
          include_fundamental: true,
        } as EnhancedTokenAnalysisRequest),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const result = await response.json();
      setAnalysisResult(result);
      setShowAnalysisInput(false);
      onAnalysisComplete?.(result);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const selectedAgent = agentConfig[agentType];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-premium"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-primary-100">
          AI Token Analysis
        </h3>
        <div className="flex items-center gap-2 text-accent-400">
          <Activity className="w-5 h-5" />
          <span className="text-sm font-medium">Live Analysis</span>
        </div>
      </div>

      {/* Agent Selection */}
      {showAnalysisInput && (
        <div className="mb-6">
          <label className="block text-sm text-primary-400 mb-3">Select AI Agent</label>
          <div className="grid grid-cols-3 gap-3">
            {Object.entries(agentConfig).map(([key, config]) => {
              const Icon = config.icon;
              const isSelected = agentType === key;
              return (
                <button
                  key={key}
                  onClick={() => setAgentType(key as 'ryu' | 'yuki' | 'sakura')}
                  className={`p-3 rounded-lg border transition-all ${
                    isSelected
                      ? 'border-accent-500 bg-accent-500/10'
                      : 'border-primary-700 bg-primary-800/30 hover:border-primary-600'
                  }`}
                >
                  <Icon className="w-5 h-5 mx-auto mb-2" style={{ color: config.color }} />
                  <div className="text-xs font-medium text-primary-200">{config.name}</div>
                  <div className="text-xs text-primary-400 mt-1 leading-tight">{config.description}</div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Token Input */}
      {showAnalysisInput && (
        <div className="mb-6">
          <label className="block text-sm text-primary-400 mb-2">Token Symbol</label>
          <div className="relative">
            <input
              type="text"
              value={tokenTicker}
              onChange={(e) => {
                setTokenTicker(e.target.value);
                setAnalysisError(null);
              }}
              onKeyPress={(e) => e.key === 'Enter' && handleAnalyzeToken()}
              placeholder="e.g., BTC, ETH, SOL, DOGE"
              className="w-full bg-primary-800/50 border border-primary-700/50 rounded-lg px-4 py-3 text-primary-100 placeholder-primary-500 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent transition-colors"
              disabled={isAnalyzing}
            />
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-primary-400" />
          </div>
          {analysisError && (
            <div className="flex items-center gap-2 mt-2 text-sm text-error-400">
              <AlertCircle className="w-4 h-4" />
              {analysisError}
            </div>
          )}
        </div>
      )}

      {/* Analysis Button */}
      {showAnalysisInput && (
        <button
          onClick={handleAnalyzeToken}
          disabled={isAnalyzing || !tokenTicker.trim()}
          className="w-full btn-primary group flex items-center justify-center gap-2 py-3"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Analyzing with {selectedAgent.name}...</span>
            </>
          ) : (
            <>
              <span>Analyze with {selectedAgent.name}</span>
              <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </>
          )}
        </button>
      )}

      {/* Analysis Results */}
      <AnimatePresence>
        {analysisResult && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="border border-primary-700/50 rounded-xl p-6 bg-primary-800/30"
          >
            {/* Token Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <SimpleTokenImage
                  symbol={analysisResult.token_ticker}
                  imageUrl={analysisResult.token_image?.small}
                  size="lg"
                />
                <div className="flex flex-col">
                  <span className="font-semibold text-primary-100 text-lg">
                    {analysisResult.token_ticker}
                  </span>
                  <span className="text-sm text-primary-400">
                    {analysisResult.token_name}
                  </span>
                  <span className="text-xs px-2 py-1 rounded-full bg-primary-700 text-primary-300 w-fit mt-1">
                    {selectedAgent.name} Analysis
                  </span>
                </div>
              </div>
              {/* Recommendation Badge */}
              <div className={`flex items-center space-x-2 px-4 py-2 rounded-full bg-primary-700 ${getRecommendationColor(analysisResult.recommendation)}`}>
                {getRecommendationIcon(analysisResult.recommendation)}
                <span className="text-sm font-semibold">
                  {analysisResult.recommendation}
                </span>
              </div>
            </div>

            {/* Current Price & Stats */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-primary-700/30 rounded-lg p-4">
                <div className="text-primary-400 text-sm mb-1">Current Price</div>
                <div className="text-primary-100 font-bold text-xl">
                  ${analysisResult.market_data.current_price.toFixed(2)}
                </div>
                <div className={`text-sm font-medium ${
                  analysisResult.market_data.price_change_percentage_24h >= 0
                    ? 'text-green-400'
                    : 'text-red-400'
                }`}>
                  {analysisResult.market_data.price_change_percentage_24h >= 0 ? '+' : ''}
                  {analysisResult.market_data.price_change_percentage_24h.toFixed(2)}% (24h)
                </div>
              </div>
              <div className="bg-primary-700/30 rounded-lg p-4">
                <div className="text-primary-400 text-sm mb-1">Risk Level</div>
                <div className={`font-bold text-lg ${
                  analysisResult.risk_level === 'LOW' ? 'text-green-400' :
                  analysisResult.risk_level === 'MEDIUM' ? 'text-amber-400' : 'text-red-400'
                }`}>
                  {analysisResult.risk_level}
                </div>
                <div className="text-primary-300 text-sm">
                  {analysisResult.risk_level === 'LOW' ? 'Conservative' :
                   analysisResult.risk_level === 'MEDIUM' ? 'Moderate' : 'Aggressive'} approach
                </div>
              </div>
            </div>

            {/* Trading Data Grid */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-primary-700/30 rounded-lg p-3">
                <div className="text-primary-400 mb-1 text-xs font-medium">Entry Range</div>
                <div className="text-primary-100 font-semibold">
                  ${analysisResult.detailed_insights.entry_strategy.entry_range_low.toFixed(2)} -
                  ${analysisResult.detailed_insights.entry_strategy.entry_range_high.toFixed(2)}
                </div>
              </div>
              <div className="bg-primary-700/30 rounded-lg p-3">
                <div className="text-primary-400 mb-1 text-xs font-medium">Stop Loss</div>
                <div className="text-red-400 font-semibold">
                  ${analysisResult.detailed_insights.risk_management.stop_loss.toFixed(2)}
                </div>
              </div>
              <div className="bg-primary-700/30 rounded-lg p-3">
                <div className="text-primary-400 mb-1 text-xs font-medium">Primary Target</div>
                <div className="text-green-400 font-semibold">
                  ${analysisResult.detailed_insights.exit_strategy.primary_target.toFixed(2)}
                </div>
              </div>
              <div className="bg-primary-700/30 rounded-lg p-3">
                <div className="text-primary-400 mb-1 text-xs font-medium">Position Size</div>
                <div className="text-primary-100 font-semibold text-xs">
                  {analysisResult.detailed_insights.risk_management.position_size_recommendation}
                </div>
              </div>
            </div>

            {/* Analysis Score */}
            <div className="mb-6 bg-primary-700/30 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-primary-300">Overall Analysis Score</span>
                <span className={`text-2xl font-bold ${getAnalysisScoreColor(analysisResult.overall_score)}`}>
                  {Math.round(analysisResult.overall_score * 100)}/100
                </span>
              </div>
              <div className="w-full bg-primary-600 rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(analysisResult.overall_score || 0) * 100}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className={`h-2 rounded-full ${
                    analysisResult.overall_score >= 0.7 ? 'bg-green-500' :
                    analysisResult.overall_score >= 0.4 ? 'bg-amber-500' : 'bg-red-500'
                  }`}
                />
              </div>
            </div>

            {/* Technical Indicators Quick View */}
            <div className="grid grid-cols-3 gap-3 mb-6 text-xs">
              <div className="text-center bg-primary-700/20 rounded-lg p-2">
                <div className="text-primary-400">RSI</div>
                <div className="text-primary-100 font-semibold">
                  {analysisResult.technical_analysis.indicators.rsi.toFixed(1)}
                </div>
              </div>
              <div className="text-center bg-primary-700/20 rounded-lg p-2">
                <div className="text-primary-400">Trend</div>
                <div className={`font-semibold ${
                  analysisResult.technical_analysis.trend === 'BULLISH' ? 'text-green-400' :
                  analysisResult.technical_analysis.trend === 'BEARISH' ? 'text-red-400' : 'text-amber-400'
                }`}>
                  {analysisResult.technical_analysis.trend}
                </div>
              </div>
              <div className="text-center bg-primary-700/20 rounded-lg p-2">
                <div className="text-primary-400">Sentiment</div>
                <div className={`font-semibold ${
                  analysisResult.sentiment_analysis.overall_sentiment === 'BULLISH' ? 'text-green-400' :
                  analysisResult.sentiment_analysis.overall_sentiment === 'BEARISH' ? 'text-red-400' : 'text-amber-400'
                }`}>
                  {analysisResult.sentiment_analysis.overall_sentiment}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => setIsAIInsightsModalOpen(true)}
                className="flex-1 bg-accent-500 hover:bg-accent-600 text-white py-3 px-4 rounded-lg font-medium transition-colors group flex items-center justify-center gap-2"
              >
                <BarChart3 className="w-4 h-4" />
                <span>View Full Analysis</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </button>
              <button
                onClick={() => {
                  setAnalysisResult(null);
                  setShowAnalysisInput(true);
                  setTokenTicker('');
                }}
                className="px-4 py-3 border border-primary-600 text-primary-300 rounded-lg hover:bg-primary-700/30 transition-colors"
              >
                New Analysis
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading State */}
      {isAnalyzing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-8"
        >
          <AnimeMascot
            mood="analyzing"
            message={`${selectedAgent.name} is analyzing ${tokenTicker}...`}
            agentColor={selectedAgent.color}
            className="mb-4"
          />
          <div className="text-sm font-medium text-primary-200 mb-1">AI Analysis in Progress</div>
          <div className="text-xs text-primary-400">Getting comprehensive insights from {selectedAgent.name}</div>

          {/* Progress Steps */}
          <div className="mt-6 space-y-2">
            <motion.div
              initial={{ opacity: 0.3 }}
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
              className="text-xs text-primary-300"
            >
              🔍 Collecting market data...
            </motion.div>
            <motion.div
              initial={{ opacity: 0.3 }}
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0.5 }}
              className="text-xs text-primary-300"
            >
              📊 Analyzing technical indicators...
            </motion.div>
            <motion.div
              initial={{ opacity: 0.3 }}
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 1 }}
              className="text-xs text-primary-300"
            >
              🧠 Generating AI insights...
            </motion.div>
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {!analysisResult && !isAnalyzing && !analysisError && showAnalysisInput && (
        <div className="text-center py-8 mt-4">
          <AnimeMascot
            mood="neutral"
            message="Ready for Smart Analysis"
            agentColor="#7C9082"
            className="mb-4"
          />
          <div className="text-sm text-primary-400 mt-2">
            Enter any crypto symbol to get personalized trading advice from our AI agents
          </div>
        </div>
      )}
    </motion.div>
  );
}