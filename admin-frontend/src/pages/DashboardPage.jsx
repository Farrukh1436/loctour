import { useEffect, useState } from "react";
import { Card, Col, Row, Segmented, Typography, Table, Input, Button, Modal, message, Space } from "antd";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { DeleteOutlined, FileOutlined, FolderOpenOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import { fetchOverview } from "../api/metrics.js";
import { fetchFileStats, bulkDeleteFiles } from "../api/files.js";

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
    active_registrations: [],
    daily_data: []
  });
  const [fileStats, setFileStats] = useState({
    total: { count: 0, size_mb: 0 },
    payment_proofs: { count: 0, size_mb: 0 },
    place_photos: { count: 0, size_mb: 0 }
  });
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [deleteCount, setDeleteCount] = useState("");

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    
    const loadData = async () => {
      try {
        const [overviewResponse, fileStatsResponse] = await Promise.all([
          fetchOverview(range),
          fetchFileStats()
        ]);
        
        if (isMounted) {
          setData(overviewResponse);
          setFileStats(fileStatsResponse);
        }
      } catch (error) {
        console.error("Error loading dashboard data:", error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    
    loadData();
    
    return () => {
      isMounted = false;
    };
  }, [range]);

  // Format daily data for the chart
  const chartData = (data.daily_data || []).map(item => ({
    date: dayjs(item.date).format("MMM DD"),
    income: item.income,
    expenses: item.expenses,
    net: item.net
  }));

  const handleBulkDelete = async () => {
    const count = parseInt(deleteCount);
    if (!count || count <= 0) {
      message.error("Please enter a valid number");
      return;
    }

    try {
      const result = await bulkDeleteFiles(count);
      message.success(`Deleted ${result.deleted_count} files, freed ${result.deleted_size_mb} MB`);
      setDeleteModalVisible(false);
      setDeleteCount("");
      
      // Reload file stats
      const newFileStats = await fetchFileStats();
      setFileStats(newFileStats);
    } catch (error) {
      message.error("Failed to delete files");
    }
  };

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

      <Card title="Financial Performance Over Time" style={{ marginBottom: 24 }} loading={loading}>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData} margin={{ left: 20, right: 20, top: 20, bottom: 20 }}>
            <defs>
              <linearGradient id="income" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#52c41a" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#52c41a" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="expenses" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff4d4f" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ff4d4f" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="net" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#1890ff" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#1890ff" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `${value.toFixed(0)} ₸`}
            />
            <Tooltip 
              formatter={(value, name) => [`${Number(value).toFixed(2)} ₸`, name]}
              labelFormatter={(label) => `Date: ${label}`}
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #d9d9d9',
                borderRadius: '6px'
              }}
            />
            <Area
              type="monotone"
              dataKey="income"
              stackId="1"
              stroke="#52c41a"
              fill="url(#income)"
              name="Income"
            />
            <Area
              type="monotone"
              dataKey="expenses"
              stackId="2"
              stroke="#ff4d4f"
              fill="url(#expenses)"
              name="Expenses"
            />
            <Area
              type="monotone"
              dataKey="net"
              stackId="3"
              stroke="#1890ff"
              fill="url(#net)"
              name="Net"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      <Card title="File Storage Management" style={{ marginBottom: 24 }} loading={loading}>
        <Row gutter={16}>
          <Col xs={24} md={8}>
            <Card size="small" title={
              <Space>
                <FileOutlined />
                <span>Total Files</span>
              </Space>
            }>
              <Title level={3}>{fileStats.total.count}</Title>
              <Text type="secondary">{fileStats.total.size_mb} MB</Text>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card size="small" title={
              <Space>
                <FolderOpenOutlined />
                <span>Payment Proofs</span>
              </Space>
            }>
              <Title level={3}>{fileStats.payment_proofs.count}</Title>
              <Text type="secondary">{fileStats.payment_proofs.size_mb} MB</Text>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card size="small" title={
              <Space>
                <FolderOpenOutlined />
                <span>Place Photos</span>
              </Space>
            }>
              <Title level={3}>{fileStats.place_photos.count}</Title>
              <Text type="secondary">{fileStats.place_photos.size_mb} MB</Text>
            </Card>
          </Col>
        </Row>
        <div style={{ marginTop: 16, textAlign: "center" }}>
          <Space>
            <Input
              placeholder="Number of oldest files to delete"
              value={deleteCount}
              onChange={(e) => setDeleteCount(e.target.value)}
              type="number"
              min="1"
              style={{ width: 250 }}
            />
            <Button
              type="primary"
              danger
              icon={<DeleteOutlined />}
              onClick={() => setDeleteModalVisible(true)}
              disabled={!deleteCount || parseInt(deleteCount) <= 0}
            >
              Delete Oldest Files
            </Button>
          </Space>
        </div>
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

      <Modal
        title="Confirm File Deletion"
        open={deleteModalVisible}
        onOk={handleBulkDelete}
        onCancel={() => setDeleteModalVisible(false)}
        okText="Delete Files"
        cancelText="Cancel"
        okButtonProps={{ danger: true }}
      >
        <p>
          Are you sure you want to delete the <strong>{deleteCount}</strong> oldest files?
        </p>
        <p style={{ color: "#666" }}>
          This action cannot be undone. Files will be permanently removed from the server.
        </p>
      </Modal>
    </div>
  );
}
