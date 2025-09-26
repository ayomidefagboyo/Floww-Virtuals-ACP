export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'online' | 'offline' | 'analyzing';
  specialty: string;
  actionLabel: string;
  resultType: string;
}

// Ryu Agent - Token Analysis
export interface TokenAnalysisRequest {
  symbol: string;
}

export interface TokenAnalysisResult {
  symbol: string;
  action: 'LONG' | 'SHORT' | 'HOLD' | 'AVOID';
  confidence: number;
  currentPrice: number;
  entryRange: {
    min: number;
    max: number;
  };
  targets: {
    target1: number;
    target2?: number;
    target3?: number;
  };
  stopLoss: number;
  riskRewardRatio: number;
  analysis: {
    technical: string;
    fundamental: string;
    sentiment: string;
    risk: string;
  };
  scores: {
    technical: number;
    fundamental: number;
    momentum: number;
    sentiment: number;
    overall: number;
  };
  timestamp: string;
}

// Enhanced Token Analysis types for the new comprehensive analysis
export interface EnhancedTokenAnalysisRequest {
  token_ticker: string;
  agent_type: 'ryu' | 'yuki' | 'sakura';
  include_sentiment?: boolean;
  include_technical?: boolean;
  include_fundamental?: boolean;
}

export interface TechnicalAnalysis {
  indicators: {
    rsi: number;
    macd: number;
    bollinger_position: number;
    moving_averages: {
      sma_20: number;
      sma_50: number;
      ema_12: number;
      ema_26: number;
    };
  };
  patterns: string[];
  support_resistance: {
    support: number;
    resistance: number;
  };
  trend: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
}

export interface FundamentalAnalysis {
  market_cap: number;
  volume_24h: number;
  circulating_supply: number;
  max_supply?: number;
  market_cap_rank: number;
  price_change_24h: number;
  price_change_7d: number;
  price_change_30d: number;
}

export interface SentimentAnalysis {
  overall_sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  sentiment_score: number;
  social_mentions: number;
  news_sentiment: number;
  fear_greed_index: number;
}

export interface MarketData {
  current_price: number;
  market_cap: number;
  volume_24h: number;
  price_change_percentage_24h: number;
  circulating_supply: number;
  total_supply?: number;
  max_supply?: number;
  ath: number;
  ath_date: string;
  atl: number;
  atl_date: string;
}

export interface AgentInsights {
  agent_type: 'ryu' | 'yuki' | 'sakura';
  personality_analysis: string;
  key_observations: string[];
  risk_assessment: string;
  timeframe_recommendation: string;
  confidence_explanation: string;
}

export interface DetailedInsights {
  entry_strategy: {
    optimal_entry: number;
    entry_range_low: number;
    entry_range_high: number;
    dollar_cost_average: boolean;
    market_order_recommended: boolean;
  };
  exit_strategy: {
    primary_target: number;
    secondary_target?: number;
    profit_taking_levels: number[];
  };
  risk_management: {
    stop_loss: number;
    position_size_recommendation: string;
    max_risk_percentage: number;
    volatility_adjusted_sizing: boolean;
  };
  market_context: {
    overall_trend: string;
    market_phase: string;
    correlation_with_btc: number;
    sector_performance: string;
  };
}

export interface EnhancedTokenAnalysisResponse {
  token_ticker: string;
  token_name: string;
  token_image?: {
    thumb: string;
    small: string;
    large: string;
  };
  analysis_timestamp: string;
  agent_type: 'ryu' | 'yuki' | 'sakura';
  overall_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  recommendation: 'BUY' | 'SELL' | 'HOLD';
  technical_analysis: TechnicalAnalysis;
  fundamental_analysis: FundamentalAnalysis;
  sentiment_analysis: SentimentAnalysis;
  market_data: MarketData;
  agent_insights: AgentInsights;
  detailed_insights: DetailedInsights;
}

// Yuki Agent - Trade Scanner
export interface TradeOpportunity {
  id: string;
  symbol: string;
  direction: 'LONG' | 'SHORT';
  confidence: number;
  entryPrice: number;
  target1: number;
  target2?: number;
  stopLoss: number;
  riskRewardRatio: number;
  timeHorizon: string;
  reasoning: string;
  keyFactors: string[];
  expiresAt: string;
}

export interface TradeScanResult {
  opportunities: TradeOpportunity[];
  totalScanned: number;
  bestOpportunity: TradeOpportunity;
  marketCondition: string;
  timestamp: string;
}

// Sakura Agent - Yield Opportunities
export interface YieldOpportunity {
  id: string;
  protocol: string;
  asset: string;
  apy: number;
  tvl: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  maturity?: string;
  minimumDeposit: number;
  strategy: string;
  projectedReturns: {
    monthly: number;
    quarterly: number;
    yearly: number;
  };
}

export interface YieldAnalysisResult {
  opportunities: YieldOpportunity[];
  totalTvlAnalyzed: number;
  bestOpportunity: YieldOpportunity;
  portfolioRecommendation: {
    allocation: Array<{
      opportunity: YieldOpportunity;
      percentage: number;
    }>;
    totalProjectedApy: number;
    riskScore: number;
  };
  timestamp: string;
}