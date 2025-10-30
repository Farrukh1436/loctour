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
  message,
  Popconfirm
} from "antd";
import { DeleteOutlined, FileOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import { useNavigate } from "react-router-dom";
import { fetchTrips, createTrip } from "../api/trips.js";
import { fetchPlaces } from "../api/places.js";
import { fetchTripFileStats, deleteTripFiles } from "../api/files.js";

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
  const [tripFileStats, setTripFileStats] = useState({});
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const loadData = async () => {
    setLoading(true);
    try {
      const [tripResponse, placeResponse] = await Promise.all([fetchTrips(), fetchPlaces()]);
      const tripsData = tripResponse.results ?? tripResponse;
      setTrips(tripsData);
      setPlaces(placeResponse.results ?? placeResponse);
      
      // Load file stats for each trip
      const fileStatsPromises = tripsData.map(async (trip) => {
        try {
          const stats = await fetchTripFileStats(trip.id);
          return { tripId: trip.id, stats };
        } catch (error) {
          return { tripId: trip.id, stats: null };
        }
      });
      
      const fileStatsResults = await Promise.all(fileStatsPromises);
      const fileStatsMap = {};
      fileStatsResults.forEach(({ tripId, stats }) => {
        fileStatsMap[tripId] = stats;
      });
      setTripFileStats(fileStatsMap);
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

  const handleDeleteTripFiles = async (tripId) => {
    try {
      const result = await deleteTripFiles(tripId);
      message.success(`Deleted ${result.deleted_count} files, freed ${result.deleted_size_mb} MB`);
      await loadData(); // Reload to refresh file stats
    } catch (error) {
      message.error("Failed to delete trip files");
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
    },
    {
      title: "Files",
      key: "files",
      render: (_, record) => {
        const stats = tripFileStats[record.id];
        if (!stats) return "-";
        return (
          <Space>
            <FileOutlined />
            <span>{stats.total.count}</span>
            <span style={{ fontSize: "12px", color: "#666" }}>
              ({stats.total.size_mb} MB)
            </span>
          </Space>
        );
      }
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, record) => {
        const stats = tripFileStats[record.id];
        const hasFiles = stats && stats.total.count > 0;
        
        return (
          <Popconfirm
            title="Delete all trip files?"
            description="This will delete all payment proofs and place photos for this trip. This action cannot be undone."
            onConfirm={() => handleDeleteTripFiles(record.id)}
            okText="Delete"
            cancelText="Cancel"
            disabled={!hasFiles}
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              disabled={!hasFiles}
              size="small"
            >
              Delete Files
            </Button>
          </Popconfirm>
        );
      }
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
