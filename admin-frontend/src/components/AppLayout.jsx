import { Layout, Avatar, Dropdown, message } from "antd";
import { UserOutlined } from "@ant-design/icons";
import SidebarNav from "./SidebarNav.jsx";
import { useAuth } from "../contexts/AuthContext.jsx";

const { Header, Content } = Layout;

export default function AppLayout({ children }) {
  const { logout, user } = useAuth();

  const handleMenuClick = ({ key }) => {
    if (key === "logout") {
      logout();
      message.success("Logged out successful");
    }
  };

  const items = [
    {
      key: "user",
      label: user ? `${user.first_name || user.username}` : "User",
      disabled: true
    },
    {
      type: "divider"
    },
    {
      key: "logout",
      label: "Log out",
      danger: true
    }
  ];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <SidebarNav />
      <Layout>
        <Header className="app-header">
          <div className="app-header-title">Admin Console</div>
          <Dropdown menu={{ items, onClick: handleMenuClick }} placement="bottomRight">
            <Avatar size="large" icon={<UserOutlined />} className="app-header-avatar" />
          </Dropdown>
        </Header>
        <Content className="app-content">{children}</Content>
      </Layout>
    </Layout>
  );
}
