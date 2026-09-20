import { useState } from 'react';
import { Tabs } from '@mantine/core';
import Sidebar from './components/Sidebar';
import AskAI from './views/AskAI';
import Placeholder from './views/Placeholder';

export default function App() {
  const [state, setState] = useState(null);
  const ticker = state?.ticker;

  return (
    <Tabs defaultValue="ask" orientation="vertical" className="app-shell">
      <Sidebar ticker={ticker} />
      <Tabs.Panel value="ask"><AskAI onResult={setState} /></Tabs.Panel>
      <Tabs.Panel value="sql"><Placeholder title="SQL Query" ticker={ticker} /></Tabs.Panel>
      <Tabs.Panel value="balance"><Placeholder title="Balance Sheet" ticker={ticker} /></Tabs.Panel>
      <Tabs.Panel value="income"><Placeholder title="Income Statement" ticker={ticker} /></Tabs.Panel>
      <Tabs.Panel value="cashflow"><Placeholder title="Cash Flow Statement" ticker={ticker} /></Tabs.Panel>
    </Tabs>
  );
}
