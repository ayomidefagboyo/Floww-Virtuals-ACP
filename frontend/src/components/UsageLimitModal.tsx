import React from 'react';
import { X, Clock, AlertTriangle, CheckCircle } from 'lucide-react';

interface UsageLimitModalProps {
  isOpen: boolean;
  onClose: () => void;
  agentName: string;
  usageInfo: {
    used_today: number;
    daily_limit: number;
    remaining: number;
    reset_time: string;
  };
}

export default function UsageLimitModal({ 
  isOpen, 
  onClose, 
  agentName, 
  usageInfo 
}: UsageLimitModalProps) {
  if (!isOpen) return null;

  const resetTime = new Date(usageInfo.reset_time).toLocaleString();
  const progressPercentage = (usageInfo.used_today / usageInfo.daily_limit) * 100;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-primary-900 border border-primary-700 rounded-xl shadow-2xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-primary-700/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-error-500/20 text-error-400">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-primary-100">
                Daily Limit Reached
              </h2>
              <p className="text-sm text-primary-400">
                {agentName} Agent
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-primary-800/50 text-primary-400 hover:text-primary-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Usage Progress */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-primary-200">Usage Today</span>
              <span className="text-sm text-primary-400">
                {usageInfo.used_today} / {usageInfo.daily_limit} requests
              </span>
            </div>
            
            <div className="w-full bg-primary-800 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-error-500 to-error-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(progressPercentage, 100)}%` }}
              />
            </div>
            
            <div className="flex items-center gap-2 text-sm text-primary-400">
              <Clock className="w-4 h-4" />
              <span>Resets at {resetTime}</span>
            </div>
          </div>

          {/* Message */}
          <div className="bg-primary-800/50 rounded-lg p-4 border border-primary-700/50">
            <div className="flex items-start gap-3">
              <div className="p-1 rounded-full bg-warning-500/20 text-warning-400 mt-0.5">
                <AlertTriangle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-primary-100 font-medium mb-1">
                  Proof of Concept Limitation
                </p>
                <p className="text-sm text-primary-300 leading-relaxed">
                  You've reached the daily limit of 3 requests for the {agentName} Agent. 
                  This is a demonstration limitation to prevent overuse. Please check back 
                  tomorrow to continue testing the AI trading agents.
                </p>
              </div>
            </div>
          </div>

          {/* Features Reminder */}
          <div className="bg-accent-500/10 rounded-lg p-4 border border-accent-500/20">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-4 h-4 text-accent-400" />
              <span className="text-sm font-medium text-accent-300">
                What you can still do:
              </span>
            </div>
            <ul className="text-sm text-primary-300 space-y-1">
              <li>• Try other agents (Ryu, Sakura) if available</li>
              <li>• View previous analysis results</li>
              <li>• Explore the dashboard features</li>
              <li>• Check back tomorrow for more requests</li>
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-2">
            <button
              onClick={onClose}
              className="flex-1 btn-primary"
            >
              Understood
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 rounded-lg border border-primary-600 text-primary-300 hover:bg-primary-800/50 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
