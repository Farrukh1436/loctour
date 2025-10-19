import { useEffect, useState } from "react";
import { Card, Col, Row, Segmented, Typography, Table } from "antd";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import dayjs from "dayjs";
import { fetchOverview } from "../api/metrics.js";

const { Title, Text } = Typography;

const rangeOptions = ["30", "60", "90"];

export default function DashboardPage() {
  const [range, setRange] = useState("30");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({
    income_total: 0,
    expenses_total: 0,
    net: 0,
    outstanding_total: 0,
    active_registrations: []
  });

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchOverview(range)
      .then((response) => {
        if (isMounted) {
          setData(response);
        }
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [range]);

  const chartData = [
    {
      name: "Income",
      value: Number(data.income_total || 0)
    },
    {
      name: "Expenses",
      value: Number(data.expenses_total || 0)
    },
    {
      name: "Net",
      value: Number(data.net || 0)
    }
  ];

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={3}>Performance Overview</Title>
        </Col>
        <Col>
          <Segmented
            options={rangeOptions}
            value={range}
            onChange={setRange}
            aria-label="Select metrics range"
          />
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} md={6}>
          <Card loading={loading} title="Income">
            <Title level={4}>{Number(data.income_total || 0).toFixed(2)} ₸</Title>
            <Text type="secondary">Total confirmed payments</Text>
          </Card>
        </Col>
        <Col xs={24} md={6}>
          <Card loading={loading} title="Expenses">
            <Title level={4}>{Number(data.expenses_total || 0).toFixed(2)} ₸</Title>
            <Text type="secondary">Recorded spendings</Text>
          </Card>
        </Col>
        <Col xs={24} md={6}>
          <Card loading={loading} title="Net">
            <Title level={4}>{Number(data.net || 0).toFixed(2)} ₸</Title>
            <Text type="secondary">Income minus expenses</Text>
          </Card>
        </Col>
        <Col xs={24} md={6}>
          <Card loading={loading} title="Outstanding">
            <Title level={4}>{Number(data.outstanding_total || 0).toFixed(2)} ₸</Title>
            <Text type="secondary">Waiting for confirmation</Text>
          </Card>
        </Col>
      </Row>

      <Card title="Financial snapshot" style={{ marginBottom: 24 }} loading={loading}>
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={chartData} margin={{ left: 0, right: 0, top: 16, bottom: 0 }}>
            <defs>
              <linearGradient id="income" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value) => `${value.toFixed(2)} ₸`} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#2563eb"
              fillOpacity={1}
              fill="url(#income)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      <Card title="Active registrations" loading={loading}>
        <Table
          rowKey="id"
          dataSource={data.active_registrations || []}
          columns={[
            {
              title: "Trip",
              dataIndex: "title"
            },
            {
              title: "Sign-ups",
              dataIndex: "signups"
            },
            {
              title: "Potential income",
              render: (_, record) => `${Number(record.signups * record.default_price).toFixed(2)} ₸`
            }
          ]}
          pagination={false}
          locale={{ emptyText: "No active registrations" }}
        />
      </Card>
    </div>
  );
}
