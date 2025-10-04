/**
 * Agent Service - API client for reliable agent system
 *
 * Provides type-safe API calls to the v2 agent system with:
 * - Automatic error handling
 * - Response validation
 * - Fallback mechanisms
 * - TypeScript support
 */

import {
  AgentStatusResponse,
  TokenAnalysisRequest,
  TokenAnalysisResponse,
  TradeScanRequest,
  TradeScanResponse,
  YieldAnalysisRequest,
  YieldAnalysisResponse,
  HealthCheckResponse,
  StreamEvent,
  AgentService
} from '@/types/agents_v2';

class AgentServiceImpl implements AgentService {
  private baseUrl: string;

  constructor(baseUrl = '/api/agents') {
    this.baseUrl = baseUrl;
  }

  /**
   * Get status of all agents
   */
  async getStatus(): Promise<AgentStatusResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/status`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to get agent status:', error);
      throw new Error(`Status check failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Analyze token with Ryu agent
   */
  async analyzeToken(request: TokenAnalysisRequest): Promise<TokenAnalysisResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/ryu/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Validate response structure
      if (data.status === 'error') {
        throw new Error(data.error || 'Token analysis failed');
      }

      return data;
    } catch (error) {
      console.error('Token analysis failed:', error);
      throw new Error(`Token analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Scan markets with Yuki agent
   */
  async scanMarkets(request: TradeScanRequest = {}): Promise<TradeScanResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/yuki/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Validate response structure
      if (data.status === 'error') {
        throw new Error(data.error || 'Market scan failed');
      }

      return data;
    } catch (error) {
      console.error('Market scan failed:', error);
      throw new Error(`Market scan failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Analyze yield opportunities with Sakura agent
   */
  async analyzeYield(request: YieldAnalysisRequest = {}): Promise<YieldAnalysisResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/sakura/yield`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Validate response structure
      if (data.status === 'error') {
        throw new Error(data.error || 'Yield analysis failed');
      }

      return data;
    } catch (error) {
      console.error('Yield analysis failed:', error);
      throw new Error(`Yield analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get system health check
   */
  async getHealth(): Promise<HealthCheckResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error(`Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Stream market scan results (Server-Sent Events)
   */
  async* streamScan(): AsyncIterable<StreamEvent> {
    let eventSource: EventSource | null = null;

    try {
      eventSource = new EventSource(`${this.baseUrl}/yuki/scan/stream`);

      const eventPromises: Promise<StreamEvent>[] = [];
      let resolveNext: ((value: StreamEvent) => void) | null = null;
      let finished = false;

      // Set up event handlers
      eventSource.onmessage = (event) => {
        if (resolveNext) {
          resolveNext({
            type: 'progress',
            data: JSON.parse(event.data)
          });
          resolveNext = null;
        }
      };

      eventSource.addEventListener('progress', (event) => {
        if (resolveNext) {
          resolveNext({
            type: 'progress',
            data: JSON.parse(event.data)
          });
          resolveNext = null;
        }
      });

      eventSource.addEventListener('opportunity', (event) => {
        if (resolveNext) {
          resolveNext({
            type: 'opportunity',
            data: JSON.parse(event.data)
          });
          resolveNext = null;
        }
      });

      eventSource.addEventListener('complete', (event) => {
        if (resolveNext) {
          resolveNext({
            type: 'complete',
            data: JSON.parse(event.data)
          });
          resolveNext = null;
        }
        finished = true;
        eventSource?.close();
      });

      eventSource.addEventListener('error', (event) => {
        if (resolveNext) {
          resolveNext({
            type: 'error',
            data: { message: 'Stream error occurred' }
          });
          resolveNext = null;
        }
        finished = true;
        eventSource?.close();
      });

      // Yield events as they come
      while (!finished) {
        const nextEvent = new Promise<StreamEvent>((resolve) => {
          resolveNext = resolve;
        });

        yield await nextEvent;
      }

    } catch (error) {
      console.error('Stream scan failed:', error);
      yield {
        type: 'error',
        data: { message: `Stream failed: ${error instanceof Error ? error.message : 'Unknown error'}` }
      };
    } finally {
      eventSource?.close();
    }
  }
}

// Create singleton instance
export const agentService = new AgentServiceImpl();

// Export types for convenience
export type {
  AgentStatusResponse,
  TokenAnalysisRequest,
  TokenAnalysisResponse,
  TradeScanRequest,
  TradeScanResponse,
  YieldAnalysisRequest,
  YieldAnalysisResponse,
  HealthCheckResponse,
  StreamEvent
};