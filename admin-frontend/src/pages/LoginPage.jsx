import { useState, useEffect } from "react";
import { Form, Input, Button, Card, Typography, message, Space } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import apiClient from "../api/client.js";
import { useAuth } from "../contexts/AuthContext.jsx";

const { Title, Text } = Typography;

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const [form] = Form.useForm();

  // Fetch CSRF token on component mount
  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        const response = await apiClient.get("/auth/csrf/");
        console.log("CSRF token fetched:", response.data);
      } catch (error) {
        console.log("CSRF token fetch:", error);
      }
    };
    fetchCsrfToken();
  }, []);

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      // Use Django's built-in authentication endpoint
      const response = await apiClient.post("/auth/login/", {
        username: values.username,
        password: values.password,
      });

      if (response.status === 200) {
        message.success("Login successful!");
        login(response.data.user);
      }
    } catch (error) {
      console.error("Login error:", error);
      if (error.response?.status === 400) {
        message.error("Invalid username or password");
      } else {
        message.error("Login failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      padding: "20px"
    }}>
      <Card
        style={{
          width: "100%",
          maxWidth: 400,
          boxShadow: "0 8px 32px rgba(0,0,0,0.1)",
          borderRadius: "12px"
        }}
        bodyStyle={{ padding: "40px 32px" }}
      >
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <div style={{ textAlign: "center" }}>
            <Title level={2} style={{ margin: 0, color: "#2563eb" }}>
              Admin Console
            </Title>
            <Text type="secondary" style={{ fontSize: "16px" }}>
              Sign in to access the dashboard
            </Text>
          </div>

          <Form
            form={form}
            name="login"
            onFinish={handleSubmit}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: "Please enter your username!" }
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Username"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: "Please enter your password!" }
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
                autoComplete="current-password"
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                style={{
                  height: "48px",
                  fontSize: "16px",
                  fontWeight: "500"
                }}
              >
                Sign In
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: "center" }}>
            <Text type="secondary" style={{ fontSize: "14px" }}>
              Use your Django admin credentials
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  );
}
