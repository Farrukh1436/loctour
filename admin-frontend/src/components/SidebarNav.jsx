import { Layout, Menu } from "antd";
import {
  PieChartOutlined,
  CalendarOutlined,
  EnvironmentOutlined,
  TeamOutlined,
  DollarOutlined,
  SettingOutlined
} from "@ant-design/icons";
import { Link, useLocation } from "react-router-dom";

const { Sider } = Layout;

const menuItems = [
  {
    key: "dashboard",
    icon: <PieChartOutlined />,
    label: <Link to="/dashboard">Dashboard</Link>
  },
  {
    key: "trips",
    icon: <CalendarOutlined />,
    label: <Link to="/trips">Trips</Link>
  },
  {
    key: "places",
    icon: <EnvironmentOutlined />,
    label: <Link to="/places">Places</Link>
  },
  {
    key: "travelers",
    icon: <TeamOutlined />,
    label: <Link to="/travelers">Travelers</Link>
  },
  {
    key: "expenses",
    icon: <DollarOutlined />,
    label: <Link to="/expenses">Finance</Link>
  },
  {
    key: "settings",
    icon: <SettingOutlined />,
    label: <Link to="/settings">Settings</Link>
  }
];

export default function SidebarNav() {
  const location = useLocation();

  const activeKey =
    menuItems.find((item) => location.pathname.startsWith(`/${item.key}`))?.key ?? "dashboard";

  return (
    <Sider breakpoint="lg" collapsedWidth="0">
      <div className="app-logo">LocTur Manager</div>
      <Menu theme="dark" mode="inline" selectedKeys={[activeKey]} items={menuItems} />
    </Sider>
  );
}
