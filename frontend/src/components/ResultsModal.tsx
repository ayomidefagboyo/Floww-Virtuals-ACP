'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  TrendingUp,
  TrendingDown,
  Target,
  Shield,
  DollarSign,
  Clock,
  BarChart3,
  Leaf,
  Zap,
  Search,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { formatCurrency, formatPercentage } from '@/utils/formatters';

interface ResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: {
    agent: string;
    data: any;
  } | null;
  yukiStream?: {
    isStreaming: boolean;
    logs: string[];
    opportunities: any[]; // raw SSE opps from backend
  };
}

// Expandable Opportunity Card Component
function OpportunityCard({ opportunity: opp }: { opportunity: any }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="card-premium cursor-pointer transition-all duration-200 hover:bg-primary-700/30">
      <div
        className="flex items-center justify-between mb-4"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <h4 className="font-semibold text-primary-100">{opp.symbol}</h4>
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            opp.direction === 'LONG' ? 'bg-success-500/20 text-success-400' : 'bg-error-500/20 text-error-400'
          }`}>
            {opp.direction}
          </span>
          <span className="text-xs text-primary-500">
            Risk: {opp.risk_level || opp.riskLevel || 'MEDIUM'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="text-sm text-primary-400">
            {typeof opp.confidence === 'number' ? (opp.confidence * 100).toFixed(0) : opp.confidence}% confidence
          </div>
          {isExpanded ?
            <ChevronUp className="w-4 h-4 text-primary-400" /> :
            <ChevronDown className="w-4 h-4 text-primary-400" />
          }
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-3">
        <div>
          <div className="text-xs text-primary-400">Entry Price</div>
          <div className="font-mono text-primary-100">{formatCurrency(opp.entryPrice || opp.entry_price)}</div>
        </div>
        <div>
          <div className="text-xs text-primary-400">Take Profit</div>
          <div className="font-mono text-success-400">{formatCurrency(opp.target1 || opp.target_1)}</div>
        </div>
        <div>
          <div className="text-xs text-primary-400">Stop Loss</div>
          <div className="font-mono text-error-400">{formatCurrency(opp.stopLoss || opp.stop_loss)}</div>
        </div>
      </div>

      <div className="text-sm text-primary-400 mb-3">{opp.reasoning}</div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t border-primary-700/50 pt-3 space-y-3"
          >
            {/* Risk/Reward Ratio */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-primary-400">Risk/Reward Ratio</div>
                <div className="text-sm font-mono text-primary-100">
                  1:{(opp.riskRewardRatio || opp.risk_reward_ratio || 0).toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-xs text-primary-400">Time Horizon</div>
                <div className="text-sm text-primary-200">{opp.timeHorizon || opp.time_horizon || 'Short-term'}</div>
              </div>
            </div>

            {/* Key Factors */}
            {(opp.keyFactors || opp.key_factors) && (
              <div>
                <div className="text-xs text-primary-400 mb-2">Key Factors</div>
                <div className="flex flex-wrap gap-1">
                  {(opp.keyFactors || opp.key_factors).map((factor: string, i: number) => (
                    <span key={i} className="px-2 py-1 bg-accent-500/10 text-accent-400 rounded text-xs">
                      {factor}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Technical Analysis */}
            {opp.technical_analysis && (
              <div>
                <div className="text-xs text-primary-400 mb-2">Technical Indicators</div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>RSI: {opp.technical_analysis.rsi_14?.toFixed(1) || 'N/A'}</div>
                  <div>MACD: {opp.technical_analysis.macd_line?.toFixed(4) || 'N/A'}</div>
                  <div>BB Position: {(opp.technical_analysis.bb_position * 100)?.toFixed(1) || 'N/A'}%</div>
                  <div>Strength: {(opp.technical_analysis.strength_score * 100)?.toFixed(0) || 'N/A'}%</div>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function ResultsModal({ isOpen, onClose, result, yukiStream }: ResultsModalProps) {
  if (!result) return null;

  const renderTokenAnalysis = (data: any) => {
    const getRecommendationColor = (action: string) => {
      switch (action) {
        case 'BUY':
        case 'LONG':
          return 'text-success-400';
        case 'SELL':
        case 'SHORT':
          return 'text-error-400';
        case 'HOLD':
        default:
          return 'text-warning-400';
      }
    };

    const getRiskLevelColor = (riskLevel: string) => {
      switch (riskLevel) {
        case 'LOW':
          return 'text-success-400';
        case 'MEDIUM':
          return 'text-warning-400';
        case 'HIGH':
        case 'EXTREME':
          return 'text-error-400';
        default:
          return 'text-primary-400';
      }
    };

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4 pb-6 border-b border-primary-700/50">
          <div className="p-3 rounded-xl bg-accent-500/10 text-accent-400">
            <Search className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-primary-100">
              {data.symbol} Analysis
            </h3>
            <p className="text-sm text-primary-400">
              Real-time AI analysis by Ryu
            </p>
          </div>
        </div>

        {/* Action, Confidence & Risk Level */}
        <div className="grid grid-cols-3 gap-4">
          <div className="card-premium">
            <div className="text-sm text-primary-400 mb-1">Recommendation</div>
            <div className={`text-xl font-bold ${getRecommendationColor(data.action)}`}>
              {data.action || 'HOLD'}
            </div>
          </div>
          <div className="card-premium">
            <div className="text-sm text-primary-400 mb-1">Confidence</div>
            <div className="text-xl font-bold text-primary-100">
              {Math.round((data.confidence || 0) * 100)}%
            </div>
          </div>
          <div className="card-premium">
            <div className="text-sm text-primary-400 mb-1">Risk Level</div>
            <div className={`text-xl font-bold ${getRiskLevelColor(data.risk_level)}`}>
              {data.risk_level || 'MEDIUM'}
            </div>
          </div>
        </div>

        {/* Current Price */}
        <div className="card-premium">
          <div className="text-center">
            <div className="text-sm text-primary-400 mb-2">Current Price</div>
            <div className="text-3xl font-bold text-primary-100">
              ${data.current_price?.toFixed(6) || '0.000000'}
            </div>
          </div>
        </div>

        {/* Entry Strategy & Risk Management */}
        {(data.entry_strategy || data.risk_management) && (
          <div className="grid grid-cols-2 gap-4">
            {data.entry_strategy && (
              <div className="card-premium">
                <h4 className="font-semibold text-primary-100 mb-3">Entry Strategy</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-primary-400">Optimal Entry:</span>
                    <span className="text-primary-100 font-mono">
                      ${data.entry_strategy.optimal_entry?.toFixed(6)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-primary-400">Entry Range:</span>
                    <span className="text-primary-100 font-mono">
                      ${data.entry_strategy.entry_range_low?.toFixed(6)} - ${data.entry_strategy.entry_range_high?.toFixed(6)}
                    </span>
                  </div>
                </div>
              </div>
            )}
            {data.risk_management && (
              <div className="card-premium">
                <h4 className="font-semibold text-primary-100 mb-3">Risk Management</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-primary-400">Stop Loss:</span>
                    <span className="text-error-400 font-mono">
                      ${data.risk_management.stop_loss?.toFixed(6)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-primary-400">Position Size:</span>
                    <span className="text-primary-100">
                      {data.risk_management.position_size}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Price Targets */}
        {data.price_targets && (
          <div className="card-premium">
            <h4 className="font-semibold text-primary-100 mb-4">Price Targets</h4>
            <div className="grid grid-cols-3 gap-4">
              {data.price_targets.target_1 && (
                <div className="text-center">
                  <div className="text-xs text-primary-400">Target 1</div>
                  <div className="text-lg font-mono text-success-400">
                    ${data.price_targets.target_1.toFixed(6)}
                  </div>
                </div>
              )}
              {data.price_targets.target_2 && (
                <div className="text-center">
                  <div className="text-xs text-primary-400">Target 2</div>
                  <div className="text-lg font-mono text-success-400">
                    ${data.price_targets.target_2.toFixed(6)}
                  </div>
                </div>
              )}
              {data.price_targets.target_3 && (
                <div className="text-center">
                  <div className="text-xs text-primary-400">Target 3</div>
                  <div className="text-lg font-mono text-success-400">
                    ${data.price_targets.target_3.toFixed(6)}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* View Insights - Real Ryu Data */}
        {data.view_insights && (
          <div className="space-y-4">
            {/* Market Analysis */}
            {data.view_insights.market_analysis && (
              <div className="card-premium">
                <h4 className="font-semibold text-primary-100 mb-3">Market Analysis</h4>
                <div className="space-y-2 text-sm text-primary-400">
                  <p>{data.view_insights.market_analysis.price_action}</p>
                  <p>{data.view_insights.market_analysis.volume_analysis}</p>
                  <p>{data.view_insights.market_analysis.range_analysis}</p>
                  {data.view_insights.market_analysis.volatility_assessment && (
                    <p>{data.view_insights.market_analysis.volatility_assessment}</p>
                  )}
                </div>
              </div>
            )}

            {/* Technical Indicators */}
            {data.view_insights.technical_indicators && (
              <div className="card-premium">
                <h4 className="font-semibold text-primary-100 mb-3">Technical Indicators</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-primary-400">RSI: </span>
                    <span className="text-primary-200">
                      {data.view_insights.technical_indicators.rsi_analysis}
                    </span>
                  </div>
                  <div>
                    <span className="text-primary-400">MACD: </span>
                    <span className="text-primary-200">
                      {data.view_insights.technical_indicators.macd_analysis}
                    </span>
                  </div>
                </div>
                <div className="mt-2 space-y-1 text-sm">
                  <div>
                    <span className="text-primary-400">Bollinger Bands: </span>
                    <span className="text-primary-200">
                      {data.view_insights.technical_indicators.bollinger_analysis}
                    </span>
                  </div>
                  <div>
                    <span className="text-primary-400">Momentum: </span>
                    <span className="text-primary-200">
                      {data.view_insights.technical_indicators.momentum_score}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* AI Insights */}
            {data.view_insights.ai_insights && (
              <div className="card-premium">
                <h4 className="font-semibold text-primary-100 mb-3">AI Reasoning</h4>
                <p className="text-sm text-primary-400 mb-3">
                  {data.view_insights.ai_insights.reasoning_summary}
                </p>
                {data.view_insights.ai_insights.key_factors && (
                  <div className="flex flex-wrap gap-2">
                    {data.view_insights.ai_insights.key_factors.map((factor: string, index: number) => (
                      <span key={index} className="px-2 py-1 bg-accent-500/10 text-accent-400 rounded-full text-xs">
                        {factor}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Risk Assessment */}
            {data.view_insights.risk_assessment && (
              <div className="card-premium">
                <h4 className="font-semibold text-primary-100 mb-3">Risk Assessment</h4>
                {data.view_insights.risk_assessment.primary_risks && (
                  <div className="space-y-1 mb-3">
                    {data.view_insights.risk_assessment.primary_risks.map((risk: string, index: number) => (
                      <div key={index} className="text-sm text-primary-400 flex items-start gap-2">
                        <span className="text-error-400 mt-1">•</span>
                        <span>{risk}</span>
                      </div>
                    ))}
                  </div>
                )}
                {data.view_insights.risk_assessment.risk_mitigation && (
                  <div className="text-sm text-primary-300 bg-primary-700/30 p-3 rounded-lg">
                    <span className="text-primary-400">Mitigation: </span>
                    {data.view_insights.risk_assessment.risk_mitigation}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Key Factors */}
        {data.key_factors && data.key_factors.length > 0 && (
          <div className="card-premium">
            <h4 className="font-semibold text-primary-100 mb-3">Key Factors</h4>
            <div className="space-y-2">
              {data.key_factors.map((factor: string, index: number) => (
                <div key={index} className="text-sm text-primary-400 flex items-start gap-2">
                  <span className="text-accent-400 mt-1">•</span>
                  <span>{factor}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Reasoning */}
        {data.reasoning && !data.view_insights?.ai_insights && (
          <div className="card-premium">
            <h4 className="font-semibold text-primary-100 mb-3">AI Analysis</h4>
            <p className="text-sm text-primary-400">{data.reasoning}</p>
          </div>
        )}
      </div>
    );
  };

  const renderTradeOpportunities = (data: any) => {
    // Merge streaming opportunities (SSE) with any static ones from result
    const streamingOpps = (yukiStream?.opportunities || []).map((o: any) => ({
      id: o.id,
      symbol: o.symbol,
      direction: o.direction,
      confidence: o.confidence,
      entryPrice: o.entry_price,
      target1: o.target_1,
      target2: o.target_2,
      stopLoss: o.stop_loss,
      riskRewardRatio: o.risk_reward_ratio,
      timeHorizon: o.time_horizon,
      reasoning: o.reasoning,
      keyFactors: o.key_factors,
      expiresAt: o.expires_at,
    }));

    const staticOpps = (data?.opportunities || []) as any[];
    const combined = streamingOpps.length > 0 ? streamingOpps : staticOpps;

    return (
    <div className="space-y-6">
      {/* Header removed to avoid duplication with modal header */}

      {/* Streaming status & logs */}
      {yukiStream && (
        <div className="card-premium">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-primary-400">Live Futures Scan</div>
            {yukiStream.isStreaming && (
              <div className="inline-flex items-center gap-2 text-xs text-accent-400">
                <span className="w-2 h-2 rounded-full bg-accent-400 animate-pulse-soft" />
                Scanning...
              </div>
            )}
          </div>
          <div className="h-24 overflow-auto rounded bg-primary-900/40 p-3 text-xs text-primary-300 space-y-1">
            {yukiStream.logs.length === 0 ? (
              <div className="text-primary-500">Waiting for updates…</div>
            ) : (
              yukiStream.logs.map((log, i) => (
                <div key={i}>• {log}</div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Market Condition - removed per request */}

      {/* Opportunities */}
      <div className="space-y-4">
        {combined.map((opp: any, index: number) => (
          <OpportunityCard key={opp.id} opportunity={opp} />
        ))}
      </div>
    </div>
  );
  };

  const renderYieldOpportunities = (data: any) => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4 pb-6 border-b border-primary-700/50">
        <div className="p-3 rounded-xl bg-accent-500/10 text-accent-400">
          <Leaf className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-xl font-semibold text-primary-100">
            Yield Opportunities
          </h3>
          <p className="text-sm text-primary-400">
            Conservative DeFi yields analyzed from ${(data.totalTvlAnalyzed / 1e9).toFixed(1)}B TVL
          </p>
        </div>
      </div>

      {/* Portfolio Recommendation */}
      <div className="card-premium">
        <h4 className="font-semibold text-primary-100 mb-4">Portfolio Recommendation</h4>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <div className="text-sm text-primary-400">Projected APY</div>
            <div className="text-2xl font-bold text-success-400">
              {formatPercentage(data.portfolio_allocation?.total_projected_apy || data.portfolioRecommendation?.totalProjectedApy || 0)}
            </div>
          </div>
          <div>
            <div className="text-sm text-primary-400">Risk Score</div>
            <div className="text-2xl font-bold text-primary-100">
              {((data.portfolio_allocation?.risk_score || data.portfolioRecommendation?.riskScore || 0) * 100).toFixed(0)}/100
            </div>
          </div>
        </div>

        {/* Investment Returns Summary */}
        {data.portfolio_allocation && (
          <div className="border-t border-primary-700/50 pt-4">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-primary-700/30 rounded-lg p-3">
                <div className="text-xs text-primary-400">Investment</div>
                <div className="text-lg font-bold text-primary-100">
                  {formatCurrency(data.portfolio_allocation.investment_amount)}
                </div>
              </div>
              <div className="bg-success-500/10 rounded-lg p-3">
                <div className="text-xs text-primary-400">Annual Return</div>
                <div className="text-lg font-bold text-success-400">
                  {formatCurrency(data.portfolio_allocation.total_annual_return)}
                </div>
              </div>
              <div className="bg-accent-500/10 rounded-lg p-3">
                <div className="text-xs text-primary-400">Monthly Return</div>
                <div className="text-lg font-bold text-accent-400">
                  {formatCurrency(data.portfolio_allocation.total_monthly_return)}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Portfolio Allocations */}
      {data.portfolio_allocation?.allocation && data.portfolio_allocation.allocation.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-semibold text-primary-100">Recommended Allocations</h4>
          {data.portfolio_allocation.allocation.map((alloc: any, index: number) => (
            <div key={index} className="card-premium">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h5 className="font-semibold text-primary-100">{alloc.protocol}</h5>
                  <p className="text-sm text-primary-400">{alloc.asset} - {alloc.strategy}</p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-success-400">
                    {formatPercentage(alloc.apy)}
                  </div>
                  <div className="text-xs text-primary-400">APY</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-3">
                <div className="bg-primary-700/20 rounded-lg p-3">
                  <div className="text-xs text-primary-400">Allocation</div>
                  <div className="text-lg font-bold text-primary-100">
                    {alloc.percentage}% ({formatCurrency(alloc.allocated_amount)})
                  </div>
                </div>
                <div className="bg-success-500/10 rounded-lg p-3">
                  <div className="text-xs text-primary-400">Expected Annual Return</div>
                  <div className="text-lg font-bold text-success-400">
                    {formatCurrency(alloc.annual_return)}
                  </div>
                </div>
              </div>

              <div className="text-center bg-accent-500/10 rounded-lg p-2">
                <div className="text-xs text-primary-400">Monthly Return</div>
                <div className="text-sm font-bold text-accent-400">
                  {formatCurrency(alloc.monthly_return)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Individual Opportunities */}
      <div className="space-y-4">
        <h4 className="font-semibold text-primary-100">All Available Opportunities</h4>
        {data.opportunities?.map((opp: any, index: number) => (
          <div key={opp.id || index} className="card-premium">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h5 className="font-semibold text-primary-100">{opp.protocol}</h5>
                <p className="text-sm text-primary-400">{opp.asset} - {opp.strategy}</p>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-success-400">
                  {formatPercentage(opp.apy)}
                </div>
                <div className="text-xs text-primary-400">APY</div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-xs text-primary-400">TVL</div>
                <div className="text-sm font-mono text-primary-100">
                  ${(opp.tvl / 1e6).toFixed(0)}M
                </div>
              </div>
              <div>
                <div className="text-xs text-primary-400">Risk Level</div>
                <div className={`text-sm font-medium ${
                  (opp.risk_level || opp.riskLevel) === 'LOW' ? 'text-success-400' :
                  (opp.risk_level || opp.riskLevel) === 'MEDIUM' ? 'text-warning-400' : 'text-error-400'
                }`}>
                  {opp.risk_level || opp.riskLevel}
                </div>
              </div>
              <div>
                <div className="text-xs text-primary-400">Min Deposit</div>
                <div className="text-sm font-mono text-primary-100">
                  {(opp.minimum_deposit || opp.minimumDeposit) < 1 ?
                    (opp.minimum_deposit || opp.minimumDeposit) :
                    formatCurrency(opp.minimum_deposit || opp.minimumDeposit)}
                </div>
              </div>
            </div>

            {/* Additional Pendle-specific info */}
            {opp.data_source === 'Pendle API' && (
              <div className="mt-3 pt-3 border-t border-primary-700/30">
                <div className="text-xs text-accent-400 mb-1">Live Pendle Data</div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>Days to Maturity: <span className="text-primary-200">{opp.days_to_maturity}</span></div>
                  <div>Sakura Score: <span className="text-primary-200">{(opp.sakura_score * 100).toFixed(0)}%</span></div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            className="bg-primary-800 rounded-2xl shadow-premium-xl max-w-4xl w-full max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-primary-700/50">
              {result.agent === 'yuki' ? (
                <div>
                  <h2 className="text-lg font-semibold text-primary-100">Futures Trading Signals</h2>
                  <p className="text-sm text-primary-400">
                    {((yukiStream?.opportunities && yukiStream.opportunities.length > 0)
                      ? yukiStream.opportunities.length
                      : (result.data?.opportunities?.length || 0))} signals found
                  </p>
                </div>
              ) : (
                <h2 className="text-lg font-semibold text-primary-100">Analysis Results</h2>
              )}
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-primary-700/50 transition-colors"
              >
                <X className="w-5 h-5 text-primary-400" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {result.agent === 'ryu' && renderTokenAnalysis(result.data)}
            {result.agent === 'yuki' && renderTradeOpportunities(result.data)}
              {result.agent === 'sakura' && renderYieldOpportunities(result.data)}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}