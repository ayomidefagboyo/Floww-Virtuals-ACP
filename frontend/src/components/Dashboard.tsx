'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  RefreshCw,
  Settings,
  Bell
} from 'lucide-react';
import AgentCard from './AgentCard';
import ResultsModal from './ResultsModal';
import { Agent } from '@/types/agents';
import { agentsService } from '@/services/api';

export default function Dashboard() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [agentStatuses, setAgentStatuses] = useState<Record<string, 'online' | 'offline' | 'analyzing'>>({});
  const [selectedResult, setSelectedResult] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progressLogs, setProgressLogs] = useState<string[]>([]);
  const [liveOpportunities, setLiveOpportunities] = useState<any[]>([]);
  const [cancelStream, setCancelStream] = useState<null | (() => void)>(null);

  // Load agents on component mount
  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const agentsData = await agentsService.getAgents();
      setAgents(agentsData);

      // Initialize agent statuses
      const statuses = agentsData.reduce((acc, agent) => ({
        ...acc,
        [agent.id]: agent.status
      }), {});
      setAgentStatuses(statuses);

      setError(null);
    } catch (error) {
      console.error('Failed to load agents:', error);
      setError('Failed to connect to AI agents');
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadAgents();
    setIsRefreshing(false);
  };

  const handleAgentAction = async (agentId: string, data?: any) => {
    // Set agent to analyzing state
    setAgentStatuses(prev => ({ ...prev, [agentId]: 'analyzing' }));
    setError(null);

    try {
      let result;

      switch (agentId) {
        case 'ryu':
          if (!data?.symbol) {
            throw new Error('Token symbol is required');
          }
          console.log(`🔍 Analyzing token: ${data.symbol}`);
          result = await agentsService.analyzeToken(data.symbol);
          break;

        case 'yuki': {
          console.log('⚡ Scanning for trade opportunities...');
          // Clear previous progressive data
          setProgressLogs([]);
          setLiveOpportunities([]);

          // Start SSE stream; also trigger a fallback full scan in parallel if needed
          let completed = false;
          const stop = agentsService.streamTrades((evt) => {
            if (evt.type === 'progress') {
              const msg = typeof evt.data === 'string' ? evt.data : evt.data?.message;
              if (msg) setProgressLogs((logs) => [...logs, msg]);
            } else if (evt.type === 'opportunity') {
              setLiveOpportunities((prev) => [...prev, evt.data]);
            } else if (evt.type === 'complete') {
              completed = true;
              setProgressLogs((logs) => [...logs, 'Scan complete']);
            } else if (evt.type === 'error') {
              setProgressLogs((logs) => [...logs, 'Stream error']);
            }
          });
          setCancelStream(() => stop);

          // Also fetch the full result once ready to populate modal in one go if desired
          try {
            result = await agentsService.scanTrades();
          } finally {
            // Close stream when full result returns or errors
            stop?.();
            setCancelStream(null);
          }
          break;
        }

        case 'sakura':
          console.log('🌸 Finding yield opportunities...');
          result = await agentsService.getYieldOpportunities();
          break;

        default:
          throw new Error(`Unknown agent: ${agentId}`);
      }

      // Show results modal
      if (result) {
        setSelectedResult({ agent: agentId, data: result });
        setIsModalOpen(true);
        console.log(`✅ ${agentId} analysis completed successfully`);
      }

    } catch (error) {
      console.error(`❌ ${agentId} analysis failed:`, error);
      setError(`${agentId.charAt(0).toUpperCase() + agentId.slice(1)} analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      // Reset agent status
      setAgentStatuses(prev => ({ ...prev, [agentId]: 'online' }));
    }
  };

  // Update agents with current statuses
  const agentsWithStatus = agents.map(agent => ({
    ...agent,
    status: agentStatuses[agent.id] || agent.status
  }));

  return (
    <div className="min-h-screen bg-primary-900">
      {/* Header */}
      <header className="border-b border-primary-800/50 backdrop-blur-sm bg-primary-900/80 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-primary-100">
                Floww <span className="text-gradient">X Virtuals</span>
              </h1>
              <p className="text-sm text-primary-400 mt-1">
                AI Trading Agents Dashboard
              </p>
            </div>

            <div className="flex items-center gap-4">
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="btn-ghost"
                title="Refresh agents"
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              </button>
              <button className="btn-ghost" title="Notifications">
                <Bell className="w-4 h-4" />
              </button>
              <button className="btn-ghost" title="Settings">
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-lg bg-error-500/10 border border-error-500/20 text-error-400"
          >
            <div className="flex items-center justify-between">
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="text-error-300 hover:text-error-200"
              >
                ✕
              </button>
            </div>
          </motion.div>
        )}

        {/* Loading State */}
        {agents.length === 0 && !error && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 animate-spin text-accent-400 mx-auto mb-4" />
              <p className="text-primary-400">Loading AI agents...</p>
            </div>
          </div>
        )}


        {/* Agents Section */}
        {agents.length > 0 && (
          <section>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {agentsWithStatus.map((agent, index) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <AgentCard
                    agent={agent}
                    onAction={handleAgentAction}
                  />
                </motion.div>
              ))}
            </div>

            {/* Live Yuki Scan Progress */}
            {(agentStatuses['yuki'] === 'analyzing' || progressLogs.length > 0 || liveOpportunities.length > 0) && (
              <div className="mt-10 p-4 rounded-lg border border-primary-800 bg-primary-900/60">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-primary-200">Yuki Scan Progress</h3>
                  {cancelStream && (
                    <button
                      className="text-xs text-error-300 hover:text-error-200"
                      onClick={() => { cancelStream?.(); setCancelStream(null); setProgressLogs((l)=>[...l,'Stream cancelled']); }}
                    >
                      Cancel stream
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-primary-400 mb-1">Logs</div>
                    <div className="h-32 overflow-auto rounded bg-primary-950/50 p-3 text-xs text-primary-300 space-y-1">
                      {progressLogs.length === 0 ? (
                        <div className="text-primary-500">Waiting for updates…</div>
                      ) : (
                        progressLogs.map((log, i) => (
                          <div key={i}>• {log}</div>
                        ))
                      )}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-primary-400 mb-1">Found Opportunities</div>
                    <div className="h-32 overflow-auto rounded bg-primary-950/50 p-3 text-xs text-primary-300 space-y-2">
                      {liveOpportunities.length === 0 ? (
                        <div className="text-primary-500">No opportunities yet…</div>
                      ) : (
                        liveOpportunities.map((o, i) => (
                          <div key={i} className="flex items-center justify-between">
                            <span className="text-primary-200">{o.symbol}</span>
                            <span className="text-primary-500">{o.direction} · {(o.confidence ?? 0).toFixed?.(2) ?? o.confidence}</span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </section>
        )}

        {/* Connection Status */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-800/50 text-primary-400 text-xs">
            <div className="w-2 h-2 rounded-full bg-success-400 animate-pulse-soft" />
            Connected to Floww Backend (Port 8001)
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-primary-800/50">
          <div className="text-center text-primary-500 text-sm">
            <p>© 2024 Floww X Virtuals. Where algorithms dream of electric sheep and crypto moons 🚀🤖</p>
          </div>
        </footer>
      </main>

      {/* Results Modal */}
      <ResultsModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        result={selectedResult}
      />
    </div>
  );
}