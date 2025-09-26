import Head from 'next/head';
import Dashboard from '@/components/Dashboard';

export default function Home() {
  return (
    <>
      <Head>
        <title>Floww Virtuals - AI Trading Agents Dashboard</title>
        <meta
          name="description"
          content="Premium AI trading agents dashboard for cryptocurrency markets. Monitor Ryu, Yuki, and LLM analysis agents with real-time performance metrics."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.svg" />
      </Head>
      <Dashboard />
    </>
  );
}