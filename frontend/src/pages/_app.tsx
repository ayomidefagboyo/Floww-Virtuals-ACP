import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import { fontVariables } from '@/styles/fonts';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className={fontVariables}>
      <Component {...pageProps} />
    </div>
  );
}