import Head from 'next/head';
import Dashboard from '@/components/Dashboard';


export default function Home() {

  return (
    <>
      <Head>
        <title>Floww Virtuals - Fully Onchain AI Trading Agents</title>
        <meta
          name="description"
          content="Fully onchain AI trading agents with embedded analysis logic. Yuki, Ryu, and Sakura agents running completely on blockchain."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.svg" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        <Dashboard />
      </div>
    </>
  );
}