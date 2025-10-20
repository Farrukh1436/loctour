import { useEffect, useState } from "react";
import {
  Button,
  Card,
  Table,
  Modal,
  Form,
  Input,
  InputNumber,
  message
} from "antd";
import { fetchPlaces, createPlace } from "../api/places.js";
import YandexMapPicker from "../components/YandexMapPicker.jsx";

export default function PlacesPage() {
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    try {
      const response = await fetchPlaces();
      setPlaces(response.results ?? response);
    } catch (error) {
      message.error("Failed to load places");
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
      await createPlace(values);
      message.success("Place added");
      form.resetFields();
      setModalVisible(false);
      await load();
    } catch (error) {
      if (!error.errorFields) {
        message.error("Could not create place");
      }
    }
  };

  return (
    <div>
      <Button type="primary" onClick={() => setModalVisible(true)} style={{ marginBottom: 16 }}>
        Add place
      </Button>
      <Card>
        <Table
          rowKey="id"
          dataSource={places}
          loading={loading}
          columns={[
            { title: "Name", dataIndex: "name" },
            { title: "Description", dataIndex: "description" },
            {
              title: "Rating",
              dataIndex: "rating",
              render: (value) => (value ? Number(value).toFixed(1) : "—")
            }
          ]}
        />
      </Card>

      <Modal
        title="Add place"
        open={modalVisible}
        onOk={handleCreate}
        onCancel={() => setModalVisible(false)}
        okText="Save"
      >
        <Form layout="vertical" form={form}>
          <Form.Item name="name" label="Name" rules={[{ required: true }]}> 
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="coordinates" label="Location">
            <YandexMapPicker
              latitude={form.getFieldValue('latitude')}
              longitude={form.getFieldValue('longitude')}
              onLatitudeChange={(value) => form.setFieldValue('latitude', value)}
              onLongitudeChange={(value) => form.setFieldValue('longitude', value)}
              height={300}
            />
          </Form.Item>
          <Form.Item name="latitude" style={{ display: 'none' }}>
            <InputNumber />
          </Form.Item>
          <Form.Item name="longitude" style={{ display: 'none' }}>
            <InputNumber />
          </Form.Item>
          <Form.Item name="rating" label="Rating">
            <InputNumber min={0} max={5} step={0.1} style={{ width: "100%" }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
