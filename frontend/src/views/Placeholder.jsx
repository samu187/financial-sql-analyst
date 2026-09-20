import { Badge, Center, Stack, Text, ThemeIcon, Title } from '@mantine/core';
import { IconLayoutDashboard } from '@tabler/icons-react';

export default function Placeholder({ title, ticker }) {
  return (
    <Stack h="100%" gap={0}>
      <header className="view-header"><Text fw={600}>{title}</Text></header>
      <Center flex={1} p="xl">
        <Stack align="center" gap="md" ta="center">
          <ThemeIcon size={56} variant="light" color="gray" radius="xl"><IconLayoutDashboard size={26} /></ThemeIcon>
          <Badge variant="light">{ticker}</Badge>
          <Title order={2}>{title}</Title>
          <Text c="dimmed">This view is coming soon.</Text>
        </Stack>
      </Center>
    </Stack>
  );
}
