import { Card, Form, Input, Button, message } from "antd";

export default function SettingsPage() {
  const [form] = Form.useForm();

  const handleSave = () => {
    message.info("Settings persistence not yet implemented");
  };

  return (
    <Card title="Bot & payment instructions">
      <Form layout="vertical" form={form} onFinish={handleSave} initialValues={{ payment_instructions: "Send payment screenshot to the bot." }}>
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
        <Button type="primary" htmlType="submit">
          Save settings
        </Button>
      </Form>
    </Card>
  );
}
