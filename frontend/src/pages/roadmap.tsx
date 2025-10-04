'use client';

import { motion } from 'framer-motion';
import { RefreshCw } from 'lucide-react';

export default function Roadmap() {
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
            </div>

            <div className="flex items-center gap-4">
              <a
                href="/"
                className="btn-ghost text-sm font-medium"
                title="Home"
              >
                Home
              </a>
              <a
                href="/roadmap"
                className="btn-ghost text-sm font-medium text-accent-400"
                title="View Roadmap"
              >
                Roadmap
              </a>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Roadmap Section */}
        <section className="mt-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold text-primary-100 mb-4">
              Product <span className="text-gradient">Roadmap</span>
            </h2>
            <p className="text-lg text-primary-400">Our journey to revolutionize AI-powered trading</p>
          </motion.div>

          <div className="space-y-8">
            {/* Phase 1 - Completed */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="card-premium border-l-4 border-success-400"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 rounded-full bg-success-400/20 flex items-center justify-center">
                    <span className="text-success-400 font-bold text-xl">✓</span>
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-2xl font-semibold text-primary-100">Phase 1: Core Agents</h3>
                    <span className="px-3 py-1 rounded-full bg-success-400/20 text-success-400 text-sm font-medium">Completed</span>
                  </div>
                  <p className="text-primary-400 mb-4">Foundation of AI trading intelligence</p>
                  <ul className="space-y-3 text-sm text-primary-300">
                    <li className="flex items-center gap-2">
                      <span className="text-success-400 text-lg">✓</span>
                      <span>Ryu Agent - Comprehensive token analysis with technical indicators</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-success-400 text-lg">✓</span>
                      <span>Yuki Agent - Real-time market scanner for trading opportunities</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-success-400 text-lg">✓</span>
                      <span>Sakura Agent - Conservative DeFi yield farming analysis</span>
                    </li>
                  </ul>
                </div>
              </div>
            </motion.div>

            {/* Phase 2 - In Progress */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="card-premium border-l-4 border-accent-400"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 rounded-full bg-accent-400/20 flex items-center justify-center">
                    <span className="text-accent-400 font-bold text-xl">2</span>
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-2xl font-semibold text-primary-100">Phase 2: On-Chain Integration</h3>
                    <span className="px-3 py-1 rounded-full bg-accent-400/20 text-accent-400 text-sm font-medium">In Progress</span>
                  </div>
                  <p className="text-primary-400 mb-4">Bringing AI intelligence on-chain</p>
                  <ul className="space-y-3 text-sm text-primary-300">
                    <li className="flex items-center gap-2">
                      <span className="text-accent-400 text-lg">⏳</span>
                      <span>Smart contract deployment on Virtuals Protocol</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-accent-400 text-lg">⏳</span>
                      <span>On-chain oracle integration for real-time data feeds</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-accent-400 text-lg">⏳</span>
                      <span>Automated trade execution with risk management</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-accent-400 text-lg">⏳</span>
                      <span>Decentralized agent governance system</span>
                    </li>
                  </ul>
                </div>
              </div>
            </motion.div>

            {/* Phase 3 - Upcoming */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="card-premium border-l-4 border-primary-600"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 rounded-full bg-primary-700/50 flex items-center justify-center">
                    <span className="text-primary-300 font-bold text-xl">3</span>
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-2xl font-semibold text-primary-100">Phase 3: Advanced Features</h3>
                    <span className="px-3 py-1 rounded-full bg-primary-700/50 text-primary-300 text-sm font-medium">Planned</span>
                  </div>
                  <p className="text-primary-400 mb-4">Next-generation trading capabilities</p>
                  <ul className="space-y-3 text-sm text-primary-300">
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>Portfolio management agent with auto-rebalancing</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>Social sentiment analysis with Twitter/Discord integration</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>Multi-chain support (Ethereum, BSC, Polygon, Arbitrum)</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>Mobile app release for iOS and Android</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>Advanced charting and technical analysis tools</span>
                    </li>
                  </ul>
                </div>
              </div>
            </motion.div>

            {/* Phase 4 - Future */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="card-premium border-l-4 border-primary-700"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 rounded-full bg-primary-800/50 flex items-center justify-center">
                    <span className="text-primary-400 font-bold text-xl">4</span>
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-2xl font-semibold text-primary-100">Phase 4: Ecosystem Expansion</h3>
                    <span className="px-3 py-1 rounded-full bg-primary-800/50 text-primary-400 text-sm font-medium">Future</span>
                  </div>
                  <p className="text-primary-400 mb-4">Building the ultimate AI trading ecosystem</p>
                  <ul className="space-y-3 text-sm text-primary-300">
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>Community-created trading agents marketplace</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>Agent staking and revenue sharing model</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>Advanced backtesting and strategy optimization tools</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>DAO governance for protocol decisions</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>Copy trading and social trading features</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="text-primary-500 text-lg">○</span>
                      <span>AI agent tournaments and competitions</span>
                    </li>
                  </ul>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Call to Action */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="mt-12 text-center card-premium bg-gradient-to-r from-accent-500/10 to-primary-800/50"
          >
            <h3 className="text-2xl font-bold text-primary-100 mb-4">
              Join Us on This Journey
            </h3>
            <p className="text-primary-400 mb-6 max-w-2xl mx-auto">
              We're building the future of AI-powered trading. Stay updated with our progress
              and be the first to access new features as they launch.
            </p>
            <div className="flex items-center justify-center gap-4">
              <a href="/" className="btn-primary px-6 py-3">
                Try Our Agents
              </a>
            </div>
          </motion.div>
        </section>

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-primary-800/50">
          <div className="text-center text-primary-500 text-sm">
            <p>© 2024 Floww X Virtuals. Where algorithms dream of electric sheep and crypto moons 🚀🤖</p>
          </div>
        </footer>
      </main>
    </div>
  );
}
