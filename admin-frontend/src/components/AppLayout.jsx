import { Layout, Avatar, Dropdown } from "antd";
import { UserOutlined } from "@ant-design/icons";
import SidebarNav from "./SidebarNav.jsx";

const { Header, Content } = Layout;

export default function AppLayout({ children }) {
  const items = [
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
          <Dropdown menu={{ items }}>
            <Avatar size="large" icon={<UserOutlined />} className="app-header-avatar" />
          </Dropdown>
        </Header>
        <Content className="app-content">{children}</Content>
      </Layout>
    </Layout>
  );
}
