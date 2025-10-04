// Updated Agent Types for v2 Reliable System

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'online' | 'offline' | 'analyzing' | 'error';
  specialty: string;
  actionLabel: string;
  resultType: string;
  capabilities: string[];
  risk_level: 'low' | 'medium' | 'high';
  last_activity?: string;
}

// Agent Status Response
export interface AgentStatusResponse {
  agents: {
    ryu: AgentStatus;
    yuki: AgentStatus;
    sakura: AgentStatus;
  };
  system: {
    status: 'online' | 'partial' | 'offline';
    version: string;
    reliability: string;
    fallback_enabled: boolean;
  };
  timestamp: string;
}

export interface AgentStatus {
  name: string;
  status: 'online' | 'offline' | 'analyzing' | 'error';
  description: string;
  capabilities: string[];
  risk_level: 'low' | 'medium' | 'high';
  last_activity: string;
}

// Base API Response
export interface ApiResponse<T = any> {
  agent: string;
  status: 'success' | 'error';
  timestamp: string;
  data?: T;
  error?: string;
  fallback_available?: boolean;
}

// Ryu Agent - Token Analysis
export interface TokenAnalysisRequest {
  symbol: string;
  analysis_type?: string;
}

export interface TokenAnalysisResponse {
  agent: 'ryu';
  symbol: string;
  analysis_type: string;
  recommendation: 'BUY' | 'SELL' | 'HOLD' | 'AVOID';
  confidence: number;
  current_price: number;
  reasoning: string;
  key_factors: string[];
  time_horizon: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME';
  entry_strategy: {
    optimal_entry: number;
    entry_range_low: number;
    entry_range_high: number;
  };
  price_targets: {
    target_1: number;
    target_2: number;
    stop_loss: number;
  };
  technical_analysis: {
    rsi_14: number;
    macd_line: number;
    bb_position: number;
    technical_score: number;
  };
  market_data: {
    price_change_24h: number;
    volume_24h: number;
    volatility: number;
  };
  expires_at: string;
  status: 'success' | 'error';
  timestamp: string;
}

// Yuki Agent - Market Scanner
export interface TradeScanRequest {
  scan_type?: string;
  pairs_limit?: number;
}

export interface TradeOpportunity {
  id: string;
  symbol: string;
  direction: 'LONG' | 'SHORT';
  confidence: number;
  entry_price: number;
  target_1: number;
  target_2?: number;
  stop_loss: number;
  risk_reward_ratio: number;
  time_horizon: string;
  reasoning: string;
  key_factors: string[];
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME';
  technical_analysis: {
    rsi_14: number;
    macd_line: number;
    bb_position: number;
    momentum_score: number;
    strength_score: number;
  };
  expires_at: string;
}

export interface TradeScanResponse {
  agent: 'yuki';
  scan_type: string;
  opportunities: TradeOpportunity[];
  total_scanned: number;
  candidates_analyzed: number;
  opportunities_found: number;
  market_condition: string;
  status: 'success' | 'error';
  timestamp: string;
}

// Sakura Agent - Yield Farming
export interface YieldAnalysisRequest {
  analysis_type?: string;
  risk_preference?: string;
  investment_amount?: number;
}

export interface YieldOpportunity {
  id: string;
  protocol: string;
  asset: string;
  strategy: string;
  apy: number;
  tvl: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  minimum_deposit: number;
  liquidity_score: number;
  sakura_score: number;
  overall_risk_score: number;
  projected_returns: {
    monthly: number;
    quarterly: number;
    yearly: number;
  };
  recommended_allocation: number;
  description: string;
  analysis_timestamp: string;
}

export interface PortfolioAllocation {
  allocations: Array<{
    opportunity_id: string;
    protocol: string;
    asset: string;
    strategy: string;
    allocation_percentage: number;
    expected_apy: number;
    risk_level: string;
    sakura_score: number;
  }>;
  total_allocation: number;
  expected_portfolio_apy: number;
  diversification_score: number;
  allocation_strategy: string;
  rebalance_frequency: string;
}

export interface YieldAnalysisResponse {
  agent: 'sakura';
  analysis_type: string;
  risk_preference: string;
  opportunities: YieldOpportunity[];
  portfolio_allocation: PortfolioAllocation;
  risk_assessment: string;
  market_summary: {
    total_opportunities: number;
    suitable_opportunities: number;
    average_apy: number;
    total_tvl_analyzed: number;
    yield_environment: string;
  };
  expected_portfolio_apy: number;
  status: 'success' | 'error';
  timestamp: string;
}

// Streaming Events for Yuki
export interface StreamEvent {
  type: 'progress' | 'opportunity' | 'complete' | 'error';
  data: any;
}

export interface ProgressEvent {
  message: string;
}

export interface OpportunityEvent extends TradeOpportunity {
  index: number;
  total: number;
}

export interface CompleteEvent {
  opportunities_found: number;
  market_condition: string;
  timestamp: string;
}

export interface ErrorEvent {
  message: string;
}

// Health Check
export interface HealthCheckResponse {
  status: 'healthy' | 'partial' | 'unhealthy' | 'error';
  agents: {
    ryu: string;
    yuki: string;
    sakura: string;
  };
  healthy_agents: number;
  total_agents: number;
  timestamp: string;
  version: string;
  error?: string;
}

// API Service Types
export interface AgentService {
  getStatus(): Promise<AgentStatusResponse>;
  analyzeToken(request: TokenAnalysisRequest): Promise<TokenAnalysisResponse>;
  scanMarkets(request: TradeScanRequest): Promise<TradeScanResponse>;
  analyzeYield(request: YieldAnalysisRequest): Promise<YieldAnalysisResponse>;
  getHealth(): Promise<HealthCheckResponse>;
  streamScan(): AsyncIterable<StreamEvent>;
}