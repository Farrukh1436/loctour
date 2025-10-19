import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Card,
  Descriptions,
  Space,
  Tag,
  Button,
  Table,
  message,
  Modal,
  Form,
  InputNumber,
  Input,
  Select
} from "antd";
import dayjs from "dayjs";
import {
  fetchTrip,
  fetchTripParticipants,
  updateTrip,
  toggleTripAnnouncement
} from "../api/trips.js";
import { updateUserTrip } from "../api/userTrips.js";

const statusOptions = ["draft", "registration", "upcoming", "completed", "cancelled"];
const userTripStatuses = ["pending", "confirmed", "rejected", "cancelled"];
const paymentStatuses = ["pending", "confirmed", "rejected"];

const backendOrigin =
  import.meta.env.VITE_BACKEND_ORIGIN ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

function resolveMediaUrl(url) {
  if (!url) {
    return "";
  }
  try {
    const target = new URL(url, backendOrigin);
    const backend = new URL(backendOrigin);
    target.protocol = backend.protocol;
    target.host = backend.host;
    return target.toString();
  } catch (error) {
    console.error("Failed to resolve media URL", error);
    return url;
  }
}

export default function TripDetailPage() {
  const { id } = useParams();
  const [trip, setTrip] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [paymentModalVisible, setPaymentModalVisible] = useState(false);
  const [currentParticipant, setCurrentParticipant] = useState(null);
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    try {
      const [tripData, participantData] = await Promise.all([
        fetchTrip(id),
        fetchTripParticipants(id)
      ]);
      setTrip(tripData);
      setParticipants(participantData.results ?? participantData);
    } catch (error) {
      message.error("Failed to load trip");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const handleUpdateStatus = async (value) => {
    try {
      await updateTrip(id, { status: value });
      message.success("Status updated");
      await load();
    } catch (error) {
      message.error("Could not update status");
    }
  };

  const handleToggleAnnouncement = async () => {
    try {
      const result = await toggleTripAnnouncement(id);
      setTrip((prev) => ({ ...prev, announce_in_channel: result.announce_in_channel }));
      message.success("Announcement flag updated");
    } catch (error) {
      message.error("Failed to update announcement flag");
    }
  };

  const openPaymentModal = (record) => {
    setCurrentParticipant(record);
    form.setFieldsValue({
      paid_amount: Number(record.paid_amount || 0),
      payment_status: record.payment_status,
      admin_comment: record.admin_comment || "",
      status: record.status
    });
    setPaymentModalVisible(true);
  };

  const handlePaymentUpdate = async () => {
    try {
      const values = await form.validateFields();
      await updateUserTrip(currentParticipant.id, values);
      message.success("Payment updated");
      setPaymentModalVisible(false);
      await load();
    } catch (error) {
      if (!error.errorFields) {
        message.error("Could not update payment");
      }
    }
  };

  if (!trip) {
    return null;
  }

  const linkCommand = `/link_trip ${trip.id}`;

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Card
        title={trip.title}
        extra={
          <Space>
            <Select
              value={trip.status}
              onChange={handleUpdateStatus}
              options={statusOptions.map((status) => ({ value: status, label: status }))}
            />
            <Button type={trip.announce_in_channel ? "primary" : "default"} onClick={handleToggleAnnouncement}>
              {trip.announce_in_channel ? "Announce enabled" : "Announce disabled"}
            </Button>
          </Space>
        }
        loading={loading}
      >
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label="Place">
            {trip.place_detail?.name || "-"}
          </Descriptions.Item>
          <Descriptions.Item label="Registration">
            {dayjs(trip.registration_start).format("MMM D")} — {dayjs(trip.registration_end).format("MMM D, YYYY")}
          </Descriptions.Item>
          <Descriptions.Item label="Trip">
            {dayjs(trip.trip_start).format("MMM D")} — {dayjs(trip.trip_end).format("MMM D, YYYY")}
          </Descriptions.Item>
          <Descriptions.Item label="Capacity">{trip.max_capacity}</Descriptions.Item>
          <Descriptions.Item label="Default price">
            {Number(trip.default_price).toFixed(2)} ₸
          </Descriptions.Item>
          <Descriptions.Item label="Participants">
            {trip.participants_count}
          </Descriptions.Item>
          <Descriptions.Item label="Group chat ID">
            {trip.group_chat_id || "—"}
          </Descriptions.Item>
          <Descriptions.Item label="Link command" span={2}>
            <code>{linkCommand}</code>
          </Descriptions.Item>
          <Descriptions.Item label="Invite link" span={2}>
            {trip.group_invite_link ? (
              <a href={trip.group_invite_link} target="_blank" rel="noreferrer">
                {trip.group_invite_link}
              </a>
            ) : (
              "—"
            )}
          </Descriptions.Item>
          <Descriptions.Item label="Bonus message" span={2}>
            {trip.bonus_message || "—"}
          </Descriptions.Item>
          <Descriptions.Item label="Description" span={2}>
            {trip.description || "No description"}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="Participants">
        <Table
          rowKey="id"
          dataSource={participants}
          loading={loading}
          columns={[
            {
              title: "Traveler",
              render: (_, record) =>
                `${record.traveler_detail.first_name} ${record.traveler_detail.last_name || ""}`.trim()
            },
            {
              title: "Phone",
              dataIndex: ["traveler_detail", "phone_number"]
            },
            {
              title: "Status",
              dataIndex: "status",
              render: (status) => <Tag>{status}</Tag>
            },
            {
              title: "Payment",
              render: (_, record) => (
                <Space>
                  <Tag color={record.payment_status === "confirmed" ? "green" : record.payment_status === "rejected" ? "red" : "gold"}>
                    {record.payment_status}
                  </Tag>
                  <span>{Number(record.paid_amount || 0).toFixed(2)} ₸</span>
                </Space>
              )
            },
            {
              title: "Proof",
              render: (_, record) => {
                if (!record.payment_proof) {
                  return "—";
                }
                const proofUrl = resolveMediaUrl(record.payment_proof);
                return (
                  <a href={proofUrl} target="_blank" rel="noreferrer">
                    View
                  </a>
                );
              }
            },
            {
              title: "Actions",
              render: (_, record) => (
                <Space>
                  <Button size="small" onClick={() => openPaymentModal(record)}>
                    Update payment
                  </Button>
                </Space>
              )
            }
          ]}
        />
      </Card>

      <Modal
        title="Update payment"
        open={paymentModalVisible}
        onOk={handlePaymentUpdate}
        onCancel={() => setPaymentModalVisible(false)}
        okText="Save"
      >
        <Form layout="vertical" form={form}>
          <Form.Item name="paid_amount" label="Paid amount" rules={[{ required: true }]}> 
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="payment_status" label="Payment status" rules={[{ required: true }]}> 
            <Select options={paymentStatuses.map((value) => ({ value, label: value }))} />
          </Form.Item>
          <Form.Item name="status" label="Registration status" rules={[{ required: true }]}>
            <Select options={userTripStatuses.map((value) => ({ value, label: value }))} />
          </Form.Item>
          <Form.Item name="admin_comment" label="Admin comment">
            <Input.TextArea placeholder="Notes for the payment" rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  );
}
