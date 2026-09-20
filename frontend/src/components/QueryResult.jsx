import { BarChart, LineChart } from '@mantine/charts';
import { Paper, Table, Text } from '@mantine/core';

const colors = ['teal.6', 'blue.6', 'grape.5', 'orange.5'];
const numbers = new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 });

export default function QueryResult({ state }) {
  if (!state.result?.length) return null;

  const chart = state.result_type === 'linechart' || state.result_type === 'barchart';
  const Chart = state.result_type === 'linechart' ? LineChart : BarChart;

  return (
    <Paper withBorder p="md" radius="lg" mt="lg" className="result-card">
      <Text size="xs" fw={600} c="dimmed" mb="lg">{state.ticker} · FINANCIAL RESULTS</Text>
      {chart ? (
        <Chart h={300} data={state.result} dataKey={state.x_column}
          series={state.y_columns.map((name, index) => ({ name, color: colors[index % colors.length] }))}
          withLegend valueFormatter={(value) => numbers.format(value)} />
      ) : (
        <Table.ScrollContainer minWidth={400}>
          <Table highlightOnHover verticalSpacing="sm">
            <Table.Thead><Table.Tr>{state.columns.map((column) => <Table.Th key={column}>{column}</Table.Th>)}</Table.Tr></Table.Thead>
            <Table.Tbody>{state.result.map((row, index) => (
              <Table.Tr key={index}>{state.columns.map((column) => (
                <Table.Td key={column}>{row[column] == null ? '—' : typeof row[column] === 'number' && column.toLowerCase() !== 'year' ? numbers.format(row[column]) : String(row[column])}</Table.Td>
              ))}</Table.Tr>
            ))}</Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      )}
    </Paper>
  );
}
