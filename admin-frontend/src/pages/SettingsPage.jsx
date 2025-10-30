import { Card, Form, Input, Button, message, Spin } from "antd";
import { useState, useEffect } from "react";
import { settingsApi } from "../api/settings";

export default function SettingsPage() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const settings = await settingsApi.getSettings();
      form.setFieldsValue({
        payment_instructions: settings.payment_instructions || "Send payment screenshot to the bot.",
        support_contacts: settings.support_contacts || ""
      });
    } catch (error) {
      console.error("Failed to load settings:", error);
      message.error("Failed to load settings");
      // Set default values if loading fails
      form.setFieldsValue({
        payment_instructions: "Send payment screenshot to the bot.",
        support_contacts: ""
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values) => {
    try {
      setSaving(true);
      await settingsApi.updateSettings(values);
      message.success("Settings saved successfully!");
    } catch (error) {
      console.error("Failed to save settings:", error);
      message.error("Failed to save settings. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card title="Bot & payment instructions">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  return (
    <Card title="Bot & payment instructions">
      <Form layout="vertical" form={form} onFinish={handleSave}>
        <Form.Item
          label="Payment instructions"
          name="payment_instructions"
          rules={[{ required: true, message: "Payment instructions are required" }]}
        >
          <Input.TextArea rows={6} />
        </Form.Item>
        <Form.Item label="Support contacts" name="support_contacts">
          <Input.TextArea rows={4} placeholder="Telegram: @loctur_support" />
        </Form.Item>
        <Button type="primary" htmlType="submit" loading={saving}>
          Save settings
        </Button>
      </Form>
    </Card>
  );
}
