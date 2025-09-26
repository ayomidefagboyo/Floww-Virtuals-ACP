import { Html, Head, Main, NextScript } from 'next/document';
import { fontVariables } from '@/styles/fonts';

export default function Document() {
  return (
    <Html lang="en" className={fontVariables}>
      <Head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </Head>
      <body className="bg-primary-900 text-primary-100">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}