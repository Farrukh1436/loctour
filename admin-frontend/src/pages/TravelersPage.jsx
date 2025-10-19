import { useEffect, useState } from "react";
import { Card, Table, Input } from "antd";
import { fetchTravelers } from "../api/travelers.js";

export default function TravelersPage() {
  const [travelers, setTravelers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  const load = async (query = "") => {
    setLoading(true);
    try {
      const params = query ? { search: query } : {};
      const response = await fetchTravelers(params);
      setTravelers(response.results ?? response);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <Card
      title="Travelers"
      extra={<Input.Search placeholder="Search" allowClear onSearch={load} onChange={(e) => setSearch(e.target.value)} />}
    >
      <Table
        rowKey="id"
        dataSource={travelers}
        loading={loading}
        columns={[
          {
            title: "Name",
            render: (_, record) => `${record.first_name} ${record.last_name || ""}`.trim()
          },
          { title: "Phone", dataIndex: "phone_number" },
          { title: "Telegram", dataIndex: "telegram_handle" },
          { title: "Notes", dataIndex: "extra_info" }
        ]}
      />
    </Card>
  );
}
