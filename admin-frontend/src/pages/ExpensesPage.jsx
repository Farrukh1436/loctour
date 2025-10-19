import { useEffect, useMemo, useState } from "react";
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Select,
  InputNumber,
  DatePicker,
  Input,
  message
} from "antd";
import { fetchExpenses, createExpense } from "../api/expenses.js";
import { fetchTrips } from "../api/trips.js";

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  const tripLookup = useMemo(() => {
    return trips.reduce((acc, trip) => {
      acc[trip.id] = trip.title;
      return acc;
    }, {});
  }, [trips]);

  const load = async () => {
    setLoading(true);
    try {
      const [expenseResponse, tripResponse] = await Promise.all([fetchExpenses(), fetchTrips()]);
      setExpenses(expenseResponse.results ?? expenseResponse);
      setTrips(tripResponse.results ?? tripResponse);
    } catch (error) {
      message.error("Failed to load expenses");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await createExpense({
        trip: values.trip,
        amount: values.amount,
        category: values.category,
        description: values.description,
        incurred_at: values.incurred_at.format("YYYY-MM-DD")
      });
      message.success("Expense recorded");
      setModalVisible(false);
      form.resetFields();
      await load();
    } catch (error) {
      if (!error.errorFields) {
        message.error("Could not save expense");
      }
    }
  };

  return (
    <div>
      <Button type="primary" onClick={() => setModalVisible(true)} style={{ marginBottom: 16 }}>
        Record expense
      </Button>
      <Card>
        <Table
          rowKey="id"
          dataSource={expenses}
          loading={loading}
          columns={[
            {
              title: "Trip",
              dataIndex: "trip",
              render: (value) => tripLookup[value] || "—"
            },
            { title: "Category", dataIndex: "category" },
            { title: "Amount", dataIndex: "amount", render: (value) => `${Number(value).toFixed(2)} ₸` },
            { title: "Date", dataIndex: "incurred_at" },
            { title: "Description", dataIndex: "description" }
          ]}
        />
      </Card>

      <Modal
        title="Record expense"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={handleCreate}
        okText="Save"
      >
        <Form layout="vertical" form={form}>
          <Form.Item name="trip" label="Trip" rules={[{ required: true }]}> 
            <Select placeholder="Select trip">
              {trips.map((trip) => (
                <Select.Option key={trip.id} value={trip.id}>
                  {trip.title}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="amount" label="Amount" rules={[{ required: true }]}> 
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="category" label="Category" initialValue="other" rules={[{ required: true }]}> 
            <Select>
              <Select.Option value="transport">Transport</Select.Option>
              <Select.Option value="accommodation">Accommodation</Select.Option>
              <Select.Option value="food">Food</Select.Option>
              <Select.Option value="activity">Activity</Select.Option>
              <Select.Option value="other">Other</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="incurred_at" label="Date" rules={[{ required: true }]}> 
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
