import { useEffect, useRef, useState } from 'react';
import { ActionIcon, Alert, Badge, Box, Button, Group, Loader, Paper, SimpleGrid, Stack, Text, Textarea, ThemeIcon, Title } from '@mantine/core';
import { IconArrowUp, IconSparkles, IconArrowUpRight } from '@tabler/icons-react';
import QueryResult from '../components/QueryResult';

const examples = ["How has Apple's revenue grown?", "Compare NVIDIA's revenue and net income", "Show Microsoft's free cash flow by year"];

export default function AskAI({ onResult }) {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const bottom = useRef(null);

  useEffect(() => { bottom.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  async function ask(event) {
    event.preventDefault();
    if (!question.trim() || loading) return;
    const submitted = question.trim();
    setMessages((previous) => [...previous, { role: 'user', text: submitted }]);
    setQuestion('');
    setError('');
    setLoading(true);
    try {
      const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: submitted, allowed_result_types: ['table', 'linechart', 'barchart'] }),
      });
      if (!response.ok) throw new Error('Could not complete your question. Please try again.');
      const state = await response.json();
      onResult(state);
      setMessages((previous) => [...previous, {
        role: 'assistant', text: state.final_message || state.message || 'No answer was returned. Try rephrasing your question.', state,
      }]);
    } catch (error) {
      setError(error.message === 'Failed to fetch' ? 'Could not reach the server. Check your connection and try again.' : error.message);
      setQuestion(submitted);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Stack className="chat-view" gap={0}>
      <Group component="header" className="view-header" justify="space-between">
        <Text fw={600}>Ask AI</Text><Badge color="gray" variant="light" size="sm">Financial research</Badge>
      </Group>
      <Box className="conversation" aria-live="polite" aria-busy={loading}>
        <Box className="conversation-inner">
          {!messages.length && (
            <Stack className="welcome" align="center" ta="center" gap="md">
              <ThemeIcon size={58} radius={18} variant="light" color="teal"><IconSparkles size={29} stroke={1.5} /></ThemeIcon>
              <Badge variant="light" color="gray" size="sm">A clearer view of the numbers</Badge>
              <Title order={1}>What would you like to explore?</Title>
              <Text c="dimmed" maw={440}>Ask about a US-listed company. Get an answer grounded in its financial statements.</Text>
              <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="sm" mt="lg" w="100%">
                {examples.map((example) => <Button key={example} variant="default" className="suggestion" onClick={() => setQuestion(example)} rightSection={<IconArrowUpRight size={16} />}>
                  {example}
                </Button>)}
              </SimpleGrid>
            </Stack>
          )}
          {messages.map((message, index) => message.role === 'user' ? (
            <Group justify="flex-end" key={index} my="xl">
              <Paper className="user-message" px="lg" py="md" radius="lg"><Text>{message.text}</Text></Paper>
            </Group>
          ) : (
            <Box key={index} className="assistant-message" my="xl">
              <Group gap="xs" mb="sm"><ThemeIcon size={25} variant="light" radius="xl"><IconSparkles size={15} /></ThemeIcon><Text fw={600} size="sm">Financial Analyst</Text></Group>
              <Text className="answer-text" lh={1.75}>{message.text}</Text>
              <QueryResult state={message.state} />
            </Box>
          ))}
          {loading && <Group gap="sm" py="lg" role="status"><Loader size="sm" type="dots" /><Text size="sm" c="dimmed">Analysing financial statements…</Text></Group>}
          {error && <Alert color="red" title="Something went wrong" my="md">{error}</Alert>}
          <div ref={bottom} />
        </Box>
      </Box>
      <Box className="composer-area">
        <Paper component="form" onSubmit={ask} className="composer" withBorder radius="xl" p="sm" shadow="xs">
          <Textarea aria-label="Your financial question" placeholder="Ask about a company’s financials…" autosize minRows={1} maxRows={5}
            variant="unstyled" value={question} onChange={(event) => setQuestion(event.currentTarget.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
                event.preventDefault();
                event.currentTarget.form.requestSubmit();
              }
            }} />
          <ActionIcon type="submit" aria-label="Send question" size={38} radius="xl" color="dark" loading={loading} disabled={!question.trim() || loading}><IconArrowUp size={20} /></ActionIcon>
        </Paper>
        <Text ta="center" size="xs" c="dimmed" mt="sm">Include a company in each question · Shift + Enter for a new line</Text>
      </Box>
    </Stack>
  );
}
