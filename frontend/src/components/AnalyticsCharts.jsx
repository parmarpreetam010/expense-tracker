import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

const COLORS = [
  "#10b981", // Emerald
  "#3b82f6", // Sky blue
  "#f59e0b", // Amber
  "#ec4899", // Pink
  "#8b5cf6", // Purple
  "#64748b", // Slate
];

export default function AnalyticsCharts({ expenses }) {
  if (!expenses || expenses.length === 0) {
    return null;
  }

  // 1. Group data by Category for the Pie/Donut Chart
  const categoryMap = {};
  expenses.forEach((item) => {
    const cat = item.category || "Other";
    const amt = Number(item.amount || 0);
    categoryMap[cat] = (categoryMap[cat] || 0) + amt;
  });

  const categoryData = Object.keys(categoryMap).map((key) => ({
    name: key,
    value: categoryMap[key],
  }));

  // 2. Group data by Month (e.g., 'Jan 2026') for the Bar Chart
  const monthMap = {};
  expenses.forEach((item) => {
    const dateObj = item.date ? new Date(item.date) : new Date();
    const monthKey = dateObj.toLocaleDateString("en-US", {
      month: "short",
      year: "numeric",
    });
    const amt = Number(item.amount || 0);
    monthMap[monthKey] = (monthMap[monthKey] || 0) + amt;
  });

  const monthlyData = Object.keys(monthMap).map((key) => ({
    month: key,
    total: monthMap[key],
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Category Breakdown Donut Chart */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
        <h3 className="text-lg font-semibold text-white mb-4">
          Category Breakdown
        </h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={4}
                dataKey="value"
              >
                {categoryData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(val) => [`₹${Number(val).toFixed(2)}`, "Total"]}
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  color: "#fff",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        {/* Legend */}
        <div className="flex flex-wrap items-center justify-center gap-3 mt-2">
          {categoryData.map((entry, index) => (
            <div key={entry.name} className="flex items-center gap-1.5 text-xs text-slate-300">
              <span
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span>{entry.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Monthly Spending Trend Bar Chart */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
        <h3 className="text-lg font-semibold text-white mb-4">
          Spending by Month
        </h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
              <YAxis
                stroke="#94a3b8"
                fontSize={12}
                tickFormatter={(val) => `₹${val}`}
              />
              <Tooltip
                formatter={(val) => [`₹${Number(val).toFixed(2)}`, "Total"]}
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  color: "#fff",
                }}
              />
              <Bar dataKey="total" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}