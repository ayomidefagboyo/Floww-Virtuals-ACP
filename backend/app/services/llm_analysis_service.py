"""
LLM-Enhanced Analysis Service

This service integrates LLMs (Claude, OpenAI, Llama) to provide advanced reasoning
for trading decisions, combining technical analysis with natural language understanding.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum
import os
from decimal import Decimal

# LLM Client imports - Anthropic Claude only
try:
    import anthropic
except ImportError:
    anthropic = None

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"


@dataclass
class MarketContext:
    """Market context for LLM analysis."""
    timestamp: datetime
    symbol: str
    current_price: float
    price_change_24h: float
    volume_24h: float
    volatility: float
    
    # Technical indicators
    rsi: float
    macd: float
    bb_position: float  # Position within Bollinger Bands (0-1)
    
    # Market sentiment
    fear_greed_index: int
    social_sentiment: str
    news_sentiment: str
    
    # Market regime context
    market_regime: str = "sideways"  # bull_market, bear_market, or sideways
    
    # Fundamental data
    market_cap: Optional[float] = None
    funding_rate: Optional[float] = None
    open_interest_change: Optional[float] = None
    
    # Recent news/events
    recent_news: List[str] = field(default_factory=list)
    market_narrative: str = ""


@dataclass
class EntryStrategy:
    """Entry strategy details."""
    optimal_entry: float
    entry_range_low: float
    entry_range_high: float
    market_order_ok: bool = False

@dataclass
class PriceTargets:
    """Price target levels."""
    target_1: Optional[float] = None
    target_2: Optional[float] = None
    target_3: Optional[float] = None

@dataclass
class RiskManagement:
    """Risk management parameters."""
    stop_loss: Optional[float] = None
    position_size: str = "5-10% of portfolio"
    max_leverage: str = "5x"

@dataclass
class LLMAnalysis:
    """Enhanced LLM analysis result with actionable trading details."""
    recommendation: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 - 1.0
    action_summary: str  # Clear one-line action
    reasoning: str
    key_factors: List[str]
    risk_assessment: str
    time_horizon: str
    entry_strategy: Optional[EntryStrategy] = None
    price_targets: Optional[PriceTargets] = None
    risk_management: Optional[RiskManagement] = None
    market_regime: str = "UNCERTAIN"
    execution_notes: str = ""
    
    # Legacy fields for backward compatibility
    position_sizing: str = "MEDIUM"
    stop_loss_level: Optional[float] = None
    take_profit_level: Optional[float] = None
    contrarian_signals: List[str] = None


class LLMAnalysisService:
    """
    Enhanced trading analysis using Large Language Models.
    
    Combines technical analysis, sentiment data, and market context
    to provide human-like reasoning for trading decisions.
    """
    
    def __init__(self, provider: LLMProvider = LLMProvider.CLAUDE):
        """Initialize LLM service."""
        self.provider = provider
        self.client = None
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Initialize Claude client
        if provider == LLMProvider.CLAUDE:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key and anthropic:
                try:
                    self.client = anthropic.Anthropic(api_key=api_key)
                    logger.info("Claude client initialized successfully")
                except TypeError as e:
                    # Handle version compatibility issue
                    logger.warning(f"Claude client initialization failed: {e}")
                    logger.info("Attempting fallback initialization...")
                    try:
                        self.client = anthropic.Client(api_key=api_key)
                        logger.info("Claude client initialized with fallback method")
                    except Exception as fallback_error:
                        logger.error(f"Claude client fallback failed: {fallback_error}")
                        self.client = None
            else:
                logger.warning("Claude API key not found or anthropic not installed")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}. Only Claude is supported.")
        
        # Analysis configuration
        self.max_context_length = 8000  # Claude-3 Haiku context limit
    
    def safe_float(self, value, fallback=0.0):
        """Safely convert a value to float, handling dicts and None values."""
        try:
            if isinstance(value, dict):
                return float(value.get('value', fallback))
            return float(value) if value is not None else fallback
        except (TypeError, ValueError):
            return fallback
        
    async def analyze_trading_opportunity(
        self, 
        context: MarketContext,
        additional_context: str = ""
    ) -> LLMAnalysis:
        """
        Analyze a trading opportunity using LLM reasoning.
        
        Args:
            context: Market context and technical data
            additional_context: Additional context like news, events
            
        Returns:
            LLM analysis with recommendation and reasoning
        """
        try:
            # Check if LLM client is available
            if not self.client:
                logger.warning("LLM client not available, using fallback analysis")
                return self._fallback_analysis(context)
            
            # Skip caching for token analysis - users typically analyze different tokens
            # and want fresh, real-time analysis for each token
            logger.info(f"Performing fresh LLM analysis for {context.symbol} (caching disabled for token analysis)")
            
            # Prepare prompt for LLM
            prompt = self._build_analysis_prompt(context, additional_context)
            
            # Get LLM response
            response = await self._query_llm(prompt)
            
            # Parse LLM response into structured analysis
            analysis = self._parse_llm_response(response, context)
            
            logger.debug(f"LLM analysis completed for {context.symbol}: {analysis.recommendation} "
                       f"(confidence: {analysis.confidence:.2f}) - Action: {analysis.action_summary}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            return self._fallback_analysis(context)
    
    def _build_analysis_prompt(self, context: MarketContext, additional_context: str = "") -> str:
        """Build comprehensive prompt for LLM analysis."""
        
        # Safe accessor functions for technical indicators
        def safe_numeric_value(value, default=0.0):
            """Safely extract numeric value from value that might be dict or numeric."""
            if isinstance(value, dict):
                return float(value.get('value', default))
            return float(value) if value is not None else default
        
        def safe_macd_value(macd_data):
            """Safely extract MACD value from dict or float."""
            try:
                if isinstance(macd_data, dict):
                    # Try multiple possible keys
                    for key in ['macd', 'value', 'signal', 'line']:
                        if key in macd_data:
                            return float(macd_data[key])
                    return 0.0  # Default if no valid key found
                elif macd_data is not None:
                    return float(macd_data)
                else:
                    return 0.0
            except (ValueError, TypeError):
                return 0.0
        
        def safe_fear_greed_value(fg_data):
            """Safely extract fear_greed_index value from dict or int."""
            try:
                if isinstance(fg_data, dict):
                    # Try multiple possible keys
                    for key in ['fear_greed_index', 'value', 'index', 'score']:
                        if key in fg_data:
                            return int(fg_data[key])
                    return 50  # Default if no valid key found
                elif fg_data is not None:
                    return int(fg_data)
                else:
                    return 50
            except (ValueError, TypeError):
                return 50

        # Calculate technical signals with safety checks
        rsi_signal = "Oversold" if context.rsi < 30 else "Overbought" if context.rsi > 70 else "Neutral"
        macd_value = safe_macd_value(context.macd)
        macd_signal = "Bullish" if macd_value > 0 else "Bearish"
        bb_signal = "Oversold" if context.bb_position < 0.2 else "Overbought" if context.bb_position > 0.8 else "Neutral"
        
        # Safely extract fear_greed_index value
        fear_greed_value = safe_fear_greed_value(context.fear_greed_index)
        
        # Determine market sentiment
        if fear_greed_value < 25:
            fear_greed_sentiment = "Extreme Fear (potential buying opportunity)"
        elif fear_greed_value > 75:
            fear_greed_sentiment = "Extreme Greed (potential selling opportunity)"
        else:
            fear_greed_sentiment = f"Neutral sentiment (index: {fear_greed_value})"
        
        prompt = f"""
You are an expert cryptocurrency futures trader analyzing {context.symbol} for potential trading opportunities. 
Provide a comprehensive analysis combining technical, fundamental, and sentiment factors.

MARKET DATA:
- Symbol: {context.symbol}
- Current Price: ${context.current_price:,.2f}
- 24h Change: {context.price_change_24h:+.2f}%
- 24h Volume: ${context.volume_24h:,.0f}
- Volatility: {context.volatility:.2%}

TECHNICAL INDICATORS:
- RSI (14): {context.rsi:.1f} ({rsi_signal})
- MACD: {macd_value:.4f} ({macd_signal})
- Bollinger Band Position: {context.bb_position:.2f} ({bb_signal})

SENTIMENT ANALYSIS:
- Fear & Greed Index: {fear_greed_sentiment}
- Social Sentiment: {context.social_sentiment}
- News Sentiment: {context.news_sentiment}

MARKET CONTEXT:
- Market Regime: {context.market_regime.upper()} (Current macro market environment)
{f"- Market Cap: ${context.market_cap:,.0f}" if context.market_cap else ""}
{f"- Funding Rate: {context.funding_rate:.4%}" if context.funding_rate else ""}
{f"- Open Interest Change: {context.open_interest_change:+.2%}" if context.open_interest_change else ""}
- Market Narrative: {context.market_narrative}

{"ADDITIONAL CONTEXT:" if additional_context else ""}
{additional_context if additional_context else ""}

Provide your analysis in this exact JSON format (ensure valid JSON syntax):
{{
    "recommendation": "BUY",
    "confidence": 0.75,
    "action_summary": "Consider buying {context.symbol} with moderate position size",
    "reasoning": "Provide specific analysis based on actual market data, not generic statements.",
    "key_factors": ["Oversold RSI conditions", "Strong fundamental support", "Positive market sentiment"],
    "risk_assessment": "MEDIUM",
    "time_horizon": "1-7 days",
    "entry_strategy": {{
        "optimal_entry": {context.current_price:.2f},
        "entry_range_low": {context.current_price * 0.98:.2f},
        "entry_range_high": {context.current_price * 1.02:.2f},
        "market_order_ok": true
    }},
    "price_targets": {{
        "target_1": {context.current_price * 1.05:.2f},
        "target_2": {context.current_price * 1.10:.2f},
        "target_3": {context.current_price * 1.15:.2f}
    }},
    "risk_management": {{
        "stop_loss": {context.current_price * 0.95:.2f},
        "position_size": "5-10% of portfolio",
        "max_leverage": "5x"
    }},
    "market_regime": "UNCERTAIN"
}}

ANALYSIS GUIDELINES:
1. Use the Market Regime to guide your analysis:
   - BULL_MARKET: Favor LONG positions, higher confidence for upside breakouts, expect strong altcoin momentum
   - BEAR_MARKET: Favor SHORT positions, lower confidence for LONG trades, expect BTC dominance and altcoin weakness  
   - SIDEWAYS: More conservative, require stronger technical confirmation, expect range-bound trading
2. Make recommendations actionable and specific
3. Provide exact price levels based on current price of ${context.current_price:,.2f}
4. Consider realistic profit targets (3-15% moves typically) within the current market regime
5. Set stop losses 2-8% from entry depending on volatility
6. Give practical execution advice for retail traders
7. Keep language simple and avoid jargon
8. Focus on risk-first approach

Remember: Users need clear, actionable guidance. Be specific about entry, targets, and stops.
"""
        
        return prompt
    
    async def analyze_trading_context(self, context: Dict[str, Any]) -> Optional['LLMAnalysis']:
        """
        Analyze trading context for opportunity enhancement (similar to technical process flow).
        
        Args:
            context: Trading context dictionary with symbol, indicators, etc.
            
        Returns:
            LLM analysis with confidence adjustments and risk factors
        """
        try:
            # Check if LLM client is available
            if not self.client:
                logger.warning("LLM client not available for trading context analysis")
                return None
            
            logger.info(f"🧠 Running AI context analysis for {context.get('symbol', 'unknown')}")
            
            # Convert context dict to MarketContext for consistency with existing flow
            market_context = MarketContext(
                timestamp=datetime.now(),
                symbol=context.get('symbol', 'UNKNOWN'),
                current_price=context.get('market_context', {}).get('price', 0.0),
                price_change_24h=context.get('market_context', {}).get('price_change_24h', 0.0),
                volume_24h=context.get('market_context', {}).get('volume_24h', 0.0),
                volatility=0.05,  # Default
                
                # Technical indicators
                rsi=context.get('technical_indicators', {}).get('rsi', 50.0),
                macd=context.get('technical_indicators', {}).get('macd', 0.0),
                bb_position=context.get('technical_indicators', {}).get('bollinger_position', 0.5),
                
                # Default sentiment values
                fear_greed_index=50,
                social_sentiment="neutral",
                news_sentiment="neutral",
                market_regime="sideways",
                market_narrative="Market analysis in progress"
            )
            
            # Build simplified prompt for context enhancement
            prompt = self._build_context_analysis_prompt(context, market_context)
            
            # Get LLM response
            response = await self._query_llm(prompt)
            
            # Parse response into analysis
            analysis = self._parse_context_response(response, context)
            
            logger.info(f"🧠 AI context analysis completed for {context.get('symbol', 'unknown')}: confidence_score={analysis.confidence:.3f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error in trading context analysis: {e}")
            return None
    
    def _build_context_analysis_prompt(self, context: Dict[str, Any], market_context: MarketContext) -> str:
        """Build prompt for trading context analysis (similar to technical flow)."""
        
        def safe_macd_value(macd_data):
            """Safely extract MACD value from dict or float."""
            try:
                if isinstance(macd_data, dict):
                    # Try multiple possible keys
                    for key in ['macd', 'value', 'signal', 'line']:
                        if key in macd_data:
                            return float(macd_data[key])
                    return 0.0  # Default if no valid key found
                elif macd_data is not None:
                    return float(macd_data)
                else:
                    return 0.0
            except (ValueError, TypeError):
                return 0.0

        def safe_fear_greed_value(fg_data):
            """Safely extract fear_greed_index value from dict or int."""
            try:
                if isinstance(fg_data, dict):
                    # Try multiple possible keys
                    for key in ['fear_greed_index', 'value', 'index', 'score']:
                        if key in fg_data:
                            return int(fg_data[key])
                    return 50  # Default if no valid key found
                elif fg_data is not None:
                    return int(fg_data)
                else:
                    return 50
            except (ValueError, TypeError):
                return 50
        
        symbol = context.get('symbol', 'UNKNOWN')
        direction = context.get('direction', 'UNKNOWN')
        confidence = context.get('confidence', 0.5)
        
        prompt = f"""
You are an expert cryptocurrency trader providing quick confidence assessment and risk analysis for {symbol}.

CURRENT OPPORTUNITY:
- Symbol: {symbol}
- Direction: {direction}
- Mathematical Confidence: {confidence:.3f}
- Current Price: ${market_context.current_price:,.2f}
- 24h Change: {market_context.price_change_24h:+.2f}%

TECHNICAL INDICATORS:
- RSI: {market_context.rsi:.1f}
- MACD: {safe_macd_value(market_context.macd):.4f}
- Bollinger Position: {context.get('technical_indicators', {}).get('bollinger_position', 0.5):.2f}

Provide a quick assessment in this exact JSON format:
{{
    "confidence_score": 0.75,
    "risk_factors": ["Factor 1", "Factor 2"],
    "enhancement_reasoning": "Brief explanation of confidence adjustment"
}}

Guidelines:
1. confidence_score should be 0.3-0.9 (will be used to adjust mathematical confidence by ±5%)
2. risk_factors should be max 2 most important concerns
3. enhancement_reasoning should be 1-2 sentences explaining your assessment
4. Consider the mathematical confidence of {confidence:.3f} and whether technical setup supports it
5. Focus on immediate risk/reward for this specific setup
"""
        
        return prompt
    
    def _parse_context_response(self, response: str, context: Dict[str, Any]) -> 'LLMAnalysis':
        """Parse AI context response into analysis object."""
        try:
            # Try to parse JSON response
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                
                # Clean JSON string
                json_str = self._clean_json_string(json_str)
                
                data = json.loads(json_str)
                
                # Validate that this isn't a generic/example response
                reasoning = data.get('enhancement_reasoning', 'AI analysis completed')
                generic_phrases = [
                    'technical indicators show oversold conditions',
                    'fundamentals remain strong',
                    'current price offers good risk-reward',
                    'Provide specific analysis based on actual',
                    'AI analysis completed',
                    'Technical analysis fallback'
                ]
                
                if any(phrase.lower() in reasoning.lower() for phrase in generic_phrases):
                    logger.warning(f"Detected generic AI response, filtering out: {reasoning}")
                    return None
                
                confidence_score = float(data.get('confidence_score', 0.5))
                risk_factors = data.get('risk_factors', [])
                
                # Also validate risk factors aren't generic
                if risk_factors and any('Technical analysis' in factor for factor in risk_factors):
                    logger.warning("Detected generic risk factors, filtering out")
                    return None
                
                # Create analysis object compatible with existing flow
                analysis = LLMAnalysis(
                    recommendation='HOLD',  # Not used in context analysis
                    confidence=confidence_score,
                    action_summary=reasoning,
                    reasoning=reasoning,
                    key_factors=risk_factors[:2],  # Limit to 2 factors
                    risk_assessment='MEDIUM',
                    time_horizon='medium'
                )
                
                # Store risk factors for enhancement
                analysis.risk_factors = risk_factors[:2]
                
                return analysis
                
        except Exception as e:
            logger.warning(f"Failed to parse AI context response: {e}")
        
        # No fallback analysis - return None if AI analysis fails
        return None
    
    async def _query_llm(self, prompt: str) -> str:
        """Query the configured LLM with the analysis prompt."""
        try:
            if not self.client:
                raise ValueError("LLM client not initialized")
            
            if self.provider == LLMProvider.CLAUDE:
                response = await asyncio.to_thread(
                    self.client.messages.create,
                    model="claude-3-haiku-20240307",  # Fast and cost-effective
                    max_tokens=1500,
                    temperature=0.1,  # Low temperature for consistent analysis
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}. Only Claude is supported.")
                
        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            raise
    
    def _parse_llm_response(self, response: str, context: MarketContext) -> LLMAnalysis:
        """Parse LLM response into structured analysis."""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                
                # Clean common JSON issues
                json_str = self._clean_json_string(json_str)
                
                # Attempt JSON parsing with multiple fallback strategies
                analysis_data = self._parse_json_with_fallbacks(json_str)
            else:
                # Fallback: parse free-form response
                return self._parse_freeform_response(response, context)
            
            # Parse nested structures
            entry_data = analysis_data.get('entry_strategy', {})
            targets_data = analysis_data.get('price_targets', {})
            risk_data = analysis_data.get('risk_management', {})
            
            # Create structured objects with null-safe float conversion
            
            entry_strategy = None
            if entry_data:
                entry_strategy = EntryStrategy(
                    optimal_entry=self.safe_float(entry_data.get('optimal_entry'), context.current_price),
                    entry_range_low=self.safe_float(entry_data.get('entry_range_low'), context.current_price * 0.98),
                    entry_range_high=self.safe_float(entry_data.get('entry_range_high'), context.current_price * 1.02),
                    market_order_ok=bool(entry_data.get('market_order_ok', False))
                )
            
            price_targets = None
            if targets_data:
                price_targets = PriceTargets(
                    target_1=self.safe_float(targets_data.get('target_1')) if targets_data.get('target_1') is not None else None,
                    target_2=self.safe_float(targets_data.get('target_2')) if targets_data.get('target_2') is not None else None,
                    target_3=self.safe_float(targets_data.get('target_3')) if targets_data.get('target_3') is not None else None
                )
            
            risk_management = None
            if risk_data:
                risk_management = RiskManagement(
                    stop_loss=self.safe_float(risk_data.get('stop_loss')) if risk_data.get('stop_loss') is not None else None,
                    position_size=risk_data.get('position_size', '5-10% of portfolio'),
                    max_leverage=risk_data.get('max_leverage', '5x')
                )
            
            # Create enhanced analysis object
            return LLMAnalysis(
                recommendation=analysis_data.get('recommendation', 'HOLD').upper(),
                confidence=max(0.0, min(1.0, self.safe_float(analysis_data.get('confidence'), 0.5))),
                action_summary=analysis_data.get('action_summary', 'Hold position - market conditions unclear'),
                reasoning=analysis_data.get('reasoning', 'LLM analysis unavailable'),
                key_factors=analysis_data.get('key_factors', []),
                risk_assessment=analysis_data.get('risk_assessment', 'MEDIUM').upper(),
                time_horizon=analysis_data.get('time_horizon', '1-7 days'),
                entry_strategy=entry_strategy,
                price_targets=price_targets,
                risk_management=risk_management,
                market_regime=analysis_data.get('market_regime', 'UNCERTAIN').upper(),
                execution_notes=analysis_data.get('execution_notes', ''),
                # Legacy fields for backward compatibility
                position_sizing=analysis_data.get('position_sizing', 'MEDIUM').upper(),
                stop_loss_level=self.safe_float(risk_data.get('stop_loss')) if risk_data and risk_data.get('stop_loss') is not None else None,
                take_profit_level=self.safe_float(targets_data.get('target_1')) if targets_data and targets_data.get('target_1') is not None else None,
                contrarian_signals=analysis_data.get('contrarian_signals', [])
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            if 'json_str' in locals():
                logger.error(f"Failed JSON string (first 200 chars): {json_str[:200]}")
                logger.error(f"Raw LLM response (first 300 chars): {response[:300]}")
            else:
                logger.error(f"Raw LLM response (first 300 chars): {response[:300]}")
            logger.info(f"Falling back to freeform parsing for {context.symbol}")
            return self._parse_freeform_response(response, context)
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean common JSON parsing issues from LLM responses."""
        import re
        
        # Remove any text before first { or after last }
        json_str = json_str.strip()
        
        # Handle completely malformed responses that start with invalid characters
        if not json_str.startswith('{') and not json_str.startswith('['):
            # Try to find JSON-like content
            match = re.search(r'(\{.*\})', json_str, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                # If no JSON structure found, return minimal valid JSON
                return '{}'
        
        # Fix common issues:
        # 1. Replace single quotes with double quotes (but not inside strings)
        # 2. Remove trailing commas before closing braces/brackets
        # 3. Fix unescaped newlines in strings
        # 4. Remove comments (// style)
        # 5. Quote unquoted property names
        # 6. Fix malformed strings
        
        # Remove comments
        json_str = re.sub(r'//.*?(?=\n|$)', '', json_str)
        
        # Fix trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Quote unquoted property names (handles the main error we're seeing)
        # This regex finds property names that aren't quoted but should be
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # Replace single quotes with double quotes for property names and strings
        # But be careful not to replace single quotes inside double-quoted strings
        def replace_quotes(match):
            content = match.group(0)
            # Only replace single quotes that are likely property delimiters
            if content.count("'") == 2 and not content.startswith('"'):
                return content.replace("'", '"')
            return content
        
        # Find quoted strings and property names
        json_str = re.sub(r"'[^']*'", replace_quotes, json_str)
        
        # Replace unescaped newlines in string values
        json_str = re.sub(r'(?<!")(\n)(?!")', r'\\n', json_str)
        
        # Fix boolean values (case insensitive)
        json_str = re.sub(r'\bTrue\b', 'true', json_str)
        json_str = re.sub(r'\bFalse\b', 'false', json_str)
        json_str = re.sub(r'\bNone\b', 'null', json_str)
        json_str = re.sub(r'\btrue\b', 'true', json_str, flags=re.IGNORECASE)
        json_str = re.sub(r'\bfalse\b', 'false', json_str, flags=re.IGNORECASE)
        json_str = re.sub(r'\bnull\b', 'null', json_str, flags=re.IGNORECASE)
        
        # Remove any remaining invalid control characters
        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
        
        # Fix missing commas between array/object elements
        json_str = re.sub(r'(\}|\])\s*(\{|\[)', r'\1,\2', json_str)
        json_str = re.sub(r'("\s*)\s*(")', r'\1,\2', json_str)
        
        return json_str
    
    def _parse_json_with_fallbacks(self, json_str: str) -> dict:
        """Attempt to parse JSON with multiple fallback strategies."""
        import json
        
        # Strategy 1: Direct parsing
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.debug(f"Direct JSON parsing failed: {e}")
        
        # Strategy 2: Try fixing common remaining issues
        try:
            # Additional cleaning for stubborn cases
            fixed_str = json_str
            
            # Fix Python-style dictionaries that slipped through
            fixed_str = fixed_str.replace("'", '"')
            
            # Fix unquoted values that should be strings
            import re
            fixed_str = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_\s]*[a-zA-Z0-9_])\s*([,}])', r': "\1"\2', fixed_str)
            
            # Fix bare words that should be strings (but not true/false/null)
            fixed_str = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_\s]*)\s*([,}])', 
                              lambda m: f': "{m.group(1)}"{m.group(2)}' 
                              if m.group(1).lower() not in ['true', 'false', 'null'] else m.group(0), 
                              fixed_str)
            
            return json.loads(fixed_str)
        except json.JSONDecodeError as e:
            logger.debug(f"Second JSON parsing attempt failed: {e}")
        
        # Strategy 3: Try with ast.literal_eval for Python-like syntax
        try:
            import ast
            # Convert to Python dict first, then to JSON-compatible dict
            python_dict = ast.literal_eval(json_str)
            # Convert to JSON string and back to ensure compatibility
            json_compatible = json.loads(json.dumps(python_dict))
            return json_compatible
        except (ValueError, SyntaxError) as e:
            logger.debug(f"AST parsing failed: {e}")
        
        # Strategy 4: Manual key-value extraction as last resort
        try:
            import re
            
            # Extract key-value pairs manually
            result = {}
            
            # Find all key-value patterns
            patterns = [
                r'"([^"]+)"\s*:\s*"([^"]*)"',  # "key": "value"
                r'"([^"]+)"\s*:\s*([0-9.]+)',  # "key": number
                r'"([^"]+)"\s*:\s*(true|false|null)',  # "key": boolean/null
                r'(\w+)\s*:\s*"([^"]*)"',      # key: "value" (unquoted key)
                r'(\w+)\s*:\s*([0-9.]+)',      # key: number (unquoted key)
                r'(\w+)\s*:\s*(true|false|null)',  # key: boolean/null (unquoted key)
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, json_str, re.IGNORECASE)
                for match in matches:
                    key, value = match
                    # Convert value types
                    if value.lower() == 'true':
                        result[key] = True
                    elif value.lower() == 'false':
                        result[key] = False
                    elif value.lower() == 'null':
                        result[key] = None
                    elif re.match(r'^[0-9.]+$', str(value)):
                        try:
                            result[key] = float(value) if '.' in str(value) else int(value)
                        except ValueError:
                            result[key] = str(value)
                    else:
                        result[key] = str(value)
            
            if result:
                logger.info(f"Manual key-value extraction succeeded, found {len(result)} pairs")
                return result
                
        except Exception as e:
            logger.debug(f"Manual extraction failed: {e}")
        
        # Final fallback: return empty dict
        logger.warning("All JSON parsing strategies failed, returning empty dict")
        return {}
    
    def _parse_freeform_response(self, response: str, context: MarketContext) -> LLMAnalysis:
        """Parse free-form LLM response as fallback."""
        # Simple keyword-based parsing for fallback
        response_lower = response.lower()
        
        # Determine recommendation
        if 'buy' in response_lower and 'strong' in response_lower:
            recommendation = 'BUY'
            confidence = 0.8
        elif 'buy' in response_lower:
            recommendation = 'BUY'
            confidence = 0.6
        elif 'sell' in response_lower and 'strong' in response_lower:
            recommendation = 'SELL'
            confidence = 0.8
        elif 'sell' in response_lower:
            recommendation = 'SELL'
            confidence = 0.6
        else:
            recommendation = 'HOLD'
            confidence = 0.5
        
        # Extract risk level
        if 'high risk' in response_lower or 'extreme' in response_lower:
            risk_assessment = 'HIGH'
        elif 'low risk' in response_lower:
            risk_assessment = 'LOW'
        else:
            risk_assessment = 'MEDIUM'
        
        return LLMAnalysis(
            recommendation=recommendation,
            confidence=confidence,
            action_summary=f"{recommendation} - {response[:100]}...",  # Short summary
            reasoning=response[:500],  # Truncate long responses
            key_factors=['LLM analysis', 'Technical indicators', 'Market context'],
            risk_assessment=risk_assessment,
            time_horizon='4-24 hours',
            entry_strategy=EntryStrategy(
                optimal_entry=context.current_price,
                entry_range_low=context.current_price * 0.98,
                entry_range_high=context.current_price * 1.02,
                market_order_ok=True
            ),
            price_targets=PriceTargets(
                target_1=context.current_price * 1.05,
                target_2=context.current_price * 1.10,
                target_3=context.current_price * 1.15
            ),
            risk_management=RiskManagement(
                stop_loss=context.current_price * 0.95,
                position_size='1-5% of portfolio',
                max_leverage='2x'
            ),
            execution_notes='LLM response was not in expected JSON format.',
            position_sizing='MEDIUM'
        )
    
    def _fallback_analysis(self, context: MarketContext) -> LLMAnalysis:
        """Provide fallback analysis when LLM is unavailable."""
        # Dynamic rule-based fallback using real market data
        recommendation = 'HOLD'
        reasoning = "LLM unavailable - using dynamic technical analysis"
        
        # Calculate dynamic confidence based on multiple indicators
        confidence_factors = []
        
        # RSI confidence factor (0.3-0.8 based on RSI extremes)
        if context.rsi < 20:  # Extremely oversold
            rsi_confidence = 0.8
        elif context.rsi < 30:  # Oversold
            rsi_confidence = 0.7
        elif context.rsi > 80:  # Extremely overbought
            rsi_confidence = 0.8
        elif context.rsi > 70:  # Overbought
            rsi_confidence = 0.7
        elif 40 <= context.rsi <= 60:  # Neutral zone
            rsi_confidence = 0.4
        else:  # Moderate zones
            rsi_confidence = 0.5
        confidence_factors.append(rsi_confidence)
        
        # Volume confidence factor (higher volume = higher confidence)
        volume_confidence = min(0.8, max(0.3, context.volume_24h / 10000000))  # Scale based on volume
        confidence_factors.append(volume_confidence)
        
        # Volatility confidence factor (moderate volatility preferred)
        if 0.02 <= context.volatility <= 0.08:  # Optimal volatility range
            volatility_confidence = 0.7
        elif context.volatility > 0.15:  # Too volatile
            volatility_confidence = 0.3
        elif context.volatility < 0.01:  # Too stable
            volatility_confidence = 0.4
        else:  # Moderate
            volatility_confidence = 0.5
        confidence_factors.append(volatility_confidence)
        
        # MACD confirmation - handle dict or float safely
        def safe_macd_value(macd_data):
            if isinstance(macd_data, dict):
                return float(macd_data.get('macd', 0.0))
            return float(macd_data) if macd_data is not None else 0.0
        
        macd_value = safe_macd_value(context.macd)
        macd_confidence = 0.6 if abs(macd_value) > 0.001 else 0.4  # Strong signal vs weak
        confidence_factors.append(macd_confidence)
        
        # Calculate weighted average confidence
        confidence = sum(confidence_factors) / len(confidence_factors)
        
        # Enhanced technical analysis with multiple confirmations
        rsi_signal = "oversold" if context.rsi < 30 else "overbought" if context.rsi > 70 else "neutral"
        macd_signal = "bullish" if macd_value > 0 else "bearish"
        momentum_signal = "positive" if context.price_change_24h > 2 else "negative" if context.price_change_24h < -2 else "neutral"
        
        # Dynamic recommendation logic
        if context.rsi < 30 and context.price_change_24h > -5 and context.volume_24h > 1000000:
            recommendation = 'BUY'
            confidence = min(0.8, confidence + 0.15)  # Boost confidence for strong signals
            reasoning = f"Oversold RSI ({context.rsi:.1f}) with limited downside and strong volume"
        elif context.rsi > 70 and context.price_change_24h > 5 and context.volatility < 0.1:
            recommendation = 'SELL'
            confidence = min(0.8, confidence + 0.15)
            reasoning = f"Overbought RSI ({context.rsi:.1f}) with strong upward movement and manageable volatility"
        elif context.rsi < 25:  # Extreme oversold
            recommendation = 'BUY'
            confidence = min(0.85, confidence + 0.2)
            reasoning = f"Extreme oversold conditions (RSI: {context.rsi:.1f}) suggest potential reversal"
        elif context.rsi > 75:  # Extreme overbought
            recommendation = 'SELL'
            confidence = min(0.85, confidence + 0.2)
            reasoning = f"Extreme overbought conditions (RSI: {context.rsi:.1f}) suggest potential correction"
        elif macd_value > 0.005 and context.price_change_24h > 0 and context.rsi < 60:
            recommendation = 'BUY'
            confidence = min(0.7, confidence + 0.1)
            reasoning = f"Bullish MACD divergence with positive momentum and room for growth"
        
        # Dynamic stop loss based on volatility and ATR estimate
        # Use volatility to calculate a more appropriate stop loss
        volatility_multiplier = max(0.02, min(0.12, context.volatility * 2))  # 2% to 12% based on volatility
        dynamic_stop_loss = context.current_price * (1 - volatility_multiplier) if recommendation == 'BUY' else context.current_price * (1 + volatility_multiplier)
        
        # Dynamic position sizing based on volatility and confidence
        if context.volatility > 0.15:  # High volatility
            position_size = "1-3% of portfolio"
        elif context.volatility > 0.08:  # Medium volatility
            position_size = f"{int(confidence * 10)}-{int(confidence * 15)}% of portfolio"
        else:  # Low volatility
            position_size = f"{int(confidence * 5)}-{int(confidence * 20)}% of portfolio"
        
        # Dynamic leverage based on volatility and market conditions
        if context.volatility > 0.20:  # Very high volatility
            max_leverage = "1x"  # No leverage in highly volatile conditions
        elif context.volatility > 0.10:  # High volatility
            max_leverage = "2x"
        elif context.volatility > 0.05:  # Medium volatility
            max_leverage = f"{min(5, int(confidence * 8))}x"
        else:  # Low volatility
            max_leverage = f"{min(10, int(confidence * 15))}x"
        
        # Dynamic price targets based on volatility and momentum
        momentum_factor = abs(context.price_change_24h) / 100 + 1  # Adjust targets based on current momentum
        volatility_factor = min(2.0, max(0.5, context.volatility * 10))  # Scale targets by volatility
        
        if recommendation == 'BUY':
            target_1 = context.current_price * (1 + (0.03 * momentum_factor * volatility_factor))
            target_2 = context.current_price * (1 + (0.06 * momentum_factor * volatility_factor))
            target_3 = context.current_price * (1 + (0.10 * momentum_factor * volatility_factor))
        else:  # SELL or HOLD
            target_1 = context.current_price * (1 + (0.02 * volatility_factor))
            target_2 = context.current_price * (1 + (0.04 * volatility_factor))
            target_3 = context.current_price * (1 + (0.07 * volatility_factor))
        
        # Dynamic risk assessment
        risk_factors = [context.volatility, 1 - confidence, abs(context.price_change_24h) / 100]
        avg_risk = sum(risk_factors) / len(risk_factors)
        
        if avg_risk > 0.12:
            risk_assessment = 'HIGH'
        elif avg_risk > 0.06:
            risk_assessment = 'MEDIUM'
        else:
            risk_assessment = 'LOW'
        
        return LLMAnalysis(
            recommendation=recommendation,
            confidence=confidence,
            action_summary=f"{recommendation} - {reasoning}",
            reasoning=reasoning,
            key_factors=[f'RSI: {rsi_signal}', f'MACD: {macd_signal}', f'Momentum: {momentum_signal}', f'Volatility: {context.volatility:.1%}'],
            risk_assessment=risk_assessment,
            time_horizon='4-24 hours',
            entry_strategy=EntryStrategy(
                optimal_entry=context.current_price,
                entry_range_low=context.current_price * (1 - volatility_multiplier/2),
                entry_range_high=context.current_price * (1 + volatility_multiplier/2),
                market_order_ok=context.volatility < 0.08  # Only allow market orders in low volatility
            ),
            price_targets=PriceTargets(
                target_1=target_1,
                target_2=target_2,
                target_3=target_3
            ),
            risk_management=RiskManagement(
                stop_loss=dynamic_stop_loss,
                position_size=position_size,
                max_leverage=max_leverage
            ),
            execution_notes=f'Dynamic analysis based on volatility ({context.volatility:.1%}), RSI ({context.rsi:.1f}), and volume.',
            position_sizing='DYNAMIC' if context.volatility > 0.08 else 'SMALL'
        )
    
    async def analyze_portfolio_signals(
        self, 
        signals: List[Dict[str, Any]], 
        market_overview: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze multiple signals using LLM for portfolio-level insights.
        
        Args:
            signals: List of individual token signals
            market_overview: Overall market context
            
        Returns:
            Portfolio-level recommendations and insights
        """
        try:
            if not signals:
                return {'portfolio_action': 'HOLD', 'reasoning': 'No signals to analyze'}
            
            # Build portfolio analysis prompt
            signals_summary = []
            for signal in signals:
                signals_summary.append(
                    f"- {signal.get('symbol', 'Unknown')}: {signal.get('recommendation', 'HOLD')} "
                    f"(confidence: {signal.get('confidence', 0.5):.2f}) - {signal.get('reasoning', '')[:100]}"
                )
            
            prompt = f"""
Analyze this portfolio of trading signals and provide overall portfolio guidance:

INDIVIDUAL SIGNALS:
{chr(10).join(signals_summary)}

MARKET OVERVIEW:
{market_overview}

Provide portfolio-level recommendations considering:
1. Signal correlation and diversification
2. Overall market regime
3. Risk concentration
4. Optimal position sizing across signals
5. Market timing considerations

Response format:
{{
    "portfolio_action": "AGGRESSIVE_BUY|BUY|HOLD|SELL|AGGRESSIVE_SELL",
    "confidence": 0.0-1.0,
    "reasoning": "Portfolio-level analysis",
    "recommended_allocation": {{"symbol": percentage}},
    "risk_level": "LOW|MEDIUM|HIGH|EXTREME",
    "market_timing": "EXCELLENT|GOOD|FAIR|POOR",
    "diversification_score": 0.0-1.0
}}
"""
            
            response = await self._query_llm(prompt)
            
            # Parse portfolio analysis
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    return json.loads(response[json_start:json_end])
            except:
                pass
            
            # Fallback portfolio analysis
            return {
                'portfolio_action': 'HOLD',
                'confidence': 0.5,
                'reasoning': 'Portfolio analysis unavailable',
                'risk_level': 'MEDIUM'
            }
            
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {e}")
            return {'portfolio_action': 'HOLD', 'reasoning': f'Analysis error: {e}'}


# Factory function
def create_llm_analysis_service(provider: str = "claude") -> LLMAnalysisService:
    """Create LLM analysis service with specified provider."""
    provider_enum = LLMProvider(provider.lower())
    return LLMAnalysisService(provider_enum)


# Integration helper for Yuki agent
async def enhance_yuki_signals_with_llm(
    signals: List[Dict[str, Any]], 
    market_data: Dict[str, Any],
    llm_service: Optional[LLMAnalysisService] = None
) -> List[Dict[str, Any]]:
    """
    Enhance Yuki's algorithmic signals with LLM reasoning.
    
    This function takes Yuki's technical analysis signals and adds
    LLM-based market context and reasoning.
    """
    if not llm_service:
        llm_service = create_llm_analysis_service()
    
    enhanced_signals = []
    
    for signal in signals:
        try:
            # Create market context for LLM
            symbol = signal.get('symbol', '')
            context = MarketContext(
                timestamp=datetime.now(),
                symbol=symbol,
                current_price=signal.get('price', 0),
                price_change_24h=signal.get('price_change_24h', 0),
                volume_24h=signal.get('volume_24h', 0),
                volatility=signal.get('volatility', 0.1),
                rsi=signal.get('rsi', 50),
                macd=signal.get('macd', 0),
                bb_position=signal.get('bb_position', 0.5),
                fear_greed_index=market_data.get('fear_greed_index', 50),
                social_sentiment=market_data.get('social_sentiment', 'neutral'),
                news_sentiment=market_data.get('news_sentiment', 'neutral'),
                market_narrative=market_data.get('market_narrative', ''),
                funding_rate=signal.get('funding_rate')
            )
            
            # Get LLM analysis
            llm_analysis = await llm_service.analyze_trading_opportunity(context)
            
            # Combine algorithmic and LLM signals
            enhanced_signal = {
                **signal,  # Original Yuki signal
                'llm_recommendation': llm_analysis.recommendation,
                'llm_confidence': llm_analysis.confidence,
                'llm_reasoning': llm_analysis.reasoning,
                'llm_risk_assessment': llm_analysis.risk_assessment,
                'combined_confidence': (signal.get('confidence', 0.5) + llm_analysis.confidence) / 2,
                'stop_loss_level': llm_analysis.stop_loss_level,
                'take_profit_level': llm_analysis.take_profit_level,
                'market_regime': llm_analysis.market_regime,
                'enhanced_by_llm': True
            }
            
            enhanced_signals.append(enhanced_signal)
            
        except Exception as e:
            logger.error(f"Error enhancing signal for {signal.get('symbol', 'unknown')}: {e}")
            # Include original signal if LLM enhancement fails
            enhanced_signals.append({**signal, 'enhanced_by_llm': False})
    
    return enhanced_signals