import { Badge, Box, Group, Stack, Tabs, Text, ThemeIcon } from '@mantine/core';
import { IconChartBar, IconCode, IconBuildingBank, IconTrendingUp, IconArrowsExchange, IconSparkles } from '@tabler/icons-react';

const views = [
  { value: 'ask', label: 'Ask AI', icon: IconSparkles },
  { value: 'sql', label: 'SQL Query', icon: IconCode },
  { value: 'balance', label: 'Balance Sheet', icon: IconBuildingBank },
  { value: 'income', label: 'Income Statement', icon: IconTrendingUp },
  { value: 'cashflow', label: 'Cash Flow Statement', icon: IconArrowsExchange },
];

export default function Sidebar({ ticker }) {
  return (
    <Stack component="aside" className="sidebar" justify="space-between">
      <Box>
        <Group gap="sm" className="brand" wrap="nowrap">
          <ThemeIcon color="dark" size={36} radius="md"><IconChartBar size={21} /></ThemeIcon>
          <Box className="sidebar-label"><Text fw={650} size="sm">Financial Analyst</Text><Text size="xs" c="dimmed">Your research workspace</Text></Box>
        </Group>
        <Text className="sidebar-label" size="xs" c="dimmed" fw={600} mb="sm" mt={40} px="sm">WORKSPACE</Text>
        <Tabs.List aria-label="Workspace views" className="navigation">
          {views.map(({ value, label, icon: Icon }) => (
            <Tabs.Tab key={value} value={value} disabled={value !== 'ask' && !ticker}
              leftSection={<Icon size={19} stroke={1.6} />} aria-label={label}
              title={value !== 'ask' && !ticker ? 'Ask about a company to unlock this view' : label}>
              <span className="sidebar-label">{label}</span>
            </Tabs.Tab>
          ))}
        </Tabs.List>
      </Box>
      <Box className="company-card">
        <Text className="sidebar-label" size="xs" c="dimmed" mb={6}>CURRENT COMPANY</Text>
        {ticker ? <Badge variant="light" color="teal" size="lg">{ticker}</Badge> : <Text size="sm" c="dimmed" className="sidebar-label">Ask a question to begin</Text>}
        <Text className="sidebar-label" size="xs" c="dimmed" mt="sm">Annual financial statements</Text>
      </Box>
    </Stack>
  );
}
