import { useEffect, useState } from "react";
import {
  Button,
  Card,
  Table,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  DatePicker,
  InputNumber,
  Select,
  message
} from "antd";
import dayjs from "dayjs";
import { useNavigate } from "react-router-dom";
import { fetchTrips, createTrip } from "../api/trips.js";
import { fetchPlaces } from "../api/places.js";

const { RangePicker } = DatePicker;

const statusColors = {
  draft: "default",
  registration: "processing",
  upcoming: "warning",
  completed: "success",
  cancelled: "error"
};

export default function TripsPage() {
  const [loading, setLoading] = useState(false);
  const [trips, setTrips] = useState([]);
  const [places, setPlaces] = useState([]);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const loadData = async () => {
    setLoading(true);
    try {
      const [tripResponse, placeResponse] = await Promise.all([fetchTrips(), fetchPlaces()]);
      setTrips(tripResponse.results ?? tripResponse);
      setPlaces(placeResponse.results ?? placeResponse);
    } catch (error) {
      message.error("Failed to load trips");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        title: values.title,
        place: values.place,
        description: values.description,
        registration_start: values.registrationRange[0].format("YYYY-MM-DD"),
        registration_end: values.registrationRange[1].format("YYYY-MM-DD"),
        trip_start: values.tripRange[0].format("YYYY-MM-DD"),
        trip_end: values.tripRange[1].format("YYYY-MM-DD"),
        default_price: values.default_price,
        max_capacity: values.max_capacity,
        status: values.status,
        bonus_message: values.bonus_message,
      };
      await createTrip(payload);
      message.success("Trip created");
      form.resetFields();
      setCreateModalVisible(false);
      await loadData();
    } catch (error) {
      if (!error.errorFields) {
        message.error("Could not create trip");
      }
    }
  };

  const columns = [
    {
      title: "Title",
      dataIndex: "title",
      key: "title",
      render: (text, record) => (
        <Button type="link" onClick={() => navigate(`/trips/${record.id}`)}>
          {text}
        </Button>
      )
    },
    {
      title: "Place",
      dataIndex: ["place_detail", "name"],
      key: "place"
    },
    {
      title: "Trip dates",
      key: "dates",
      render: (_, record) =>
        `${dayjs(record.trip_start).format("MMM D")} - ${dayjs(record.trip_end).format("MMM D, YYYY")}`
    },
    {
      title: "Registration",
      key: "registration",
      render: (_, record) =>
        `${dayjs(record.registration_start).format("MMM D")} - ${dayjs(record.registration_end).format("MMM D")}`
    },
    {
      title: "Price",
      dataIndex: "default_price",
      key: "price",
      render: (price) => `${Number(price).toFixed(2)} ₸`
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status) => <Tag color={statusColors[status] || "default"}>{status}</Tag>
    },
    {
      title: "Participants",
      dataIndex: "participants_count",
      key: "participants"
    }
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={() => setCreateModalVisible(true)}>
          New trip
        </Button>
      </Space>

      <Card>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={trips}
          columns={columns}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="Create trip"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        onOk={handleCreate}
        okText="Create"
      >
        <Form layout="vertical" form={form}>
          <Form.Item name="title" label="Title" rules={[{ required: true }]}> 
            <Input />
          </Form.Item>
          <Form.Item name="place" label="Place" rules={[{ required: true, message: "Select a place" }]}> 
            <Select placeholder="Select place">
              {places.map((place) => (
                <Select.Option key={place.id} value={place.id}>
                  {place.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item
            name="registrationRange"
            label="Registration period"
            rules={[{ required: true, message: "Set registration period" }]}
          >
            <RangePicker />
          </Form.Item>
          <Form.Item name="tripRange" label="Trip dates" rules={[{ required: true }]}> 
            <RangePicker />
          </Form.Item>
          <Form.Item name="default_price" label="Default price" rules={[{ required: true }]}> 
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="max_capacity" label="Max capacity" rules={[{ required: true }]}> 
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Telegram group setup">
            <span className="ant-form-text">
              Add the bot to the group and run <code>/link_trip {"<trip-id>"}</code> inside Telegram to connect it.
            </span>
          </Form.Item>
          <Form.Item name="status" label="Status" initialValue="draft" rules={[{ required: true }]}> 
            <Select>
              {Object.keys(statusColors).map((status) => (
                <Select.Option key={status} value={status}>
                  {status}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="bonus_message" label="Bonus message">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
