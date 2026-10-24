import { useState, useEffect } from "react";
import { 
  PlusCircle, Trash2, Edit3, Download, LogOut, 
  AlertTriangle, CheckCircle2, TrendingUp 
} from "lucide-react";
import API from "../services/api";
import AnalyticsCharts from "./AnalyticsCharts";
import { exportExpensesToCSV } from "../utils/exportCsv";

export default function Dashboard({ onLogout }) {
  const [expenses, setExpenses] = useState([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [loading, setLoading] = useState(false);

  // Form State
  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("Food");
  const [dateVal, setDateVal] = useState(new Date().toISOString().split("T")[0]);

  // Edit State
  const [editingExpense, setEditingExpense] = useState(null);

  // Budget State
  const [budgetStatus, setBudgetStatus] = useState({
    monthly_limit: 0,
    actual_spending: 0,
    percentage_used: 0,
    status: "SAFE",
  });
  const [newBudgetLimit, setNewBudgetLimit] = useState("");
  const [budgetCategory, setBudgetCategory] = useState("1");
  const [showBudgetModal, setShowBudgetModal] = useState(false);

  // Automatically generates "YYYY-MM" (e.g., "2026-10")
  const getCurrentMonthString = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    return `${year}-${month}`;
  };

  const fetchExpenses = async () => {
    try {
      const res = await API.get("/expenses?limit=100&offset=0");
      setExpenses(res.data.data || []);
      setTotalRecords(res.data.total_records || 0);
    } catch (err) {
      console.error("Failed to fetch expenses", err);
    }
  };

  const fetchBudgetStatus = async () => {
    try {
      const res = await API.get("/budgets/status");
      setBudgetStatus(res.data);
      if (res.data.monthly_limit > 0) {
        setNewBudgetLimit(res.data.monthly_limit);
      }
    } catch (err) {
      console.error("Failed to fetch budget status", err);
    }
  };

  useEffect(() => {
    fetchExpenses();
    fetchBudgetStatus();
  }, []);

  const handleSaveExpense = async (e) => {
    e.preventDefault();
    if (!title || !amount) return;

    setLoading(true);
    try {
      if (editingExpense) {
        await API.put(`/expenses/${editingExpense.id}`, {
          title,
          amount: parseFloat(amount),
          category,
          date: dateVal,
        });
        setEditingExpense(null);
      } else {
        await API.post("/expenses", {
          title,
          amount: parseFloat(amount),
          category,
          date: dateVal,
        });
      }
      setTitle("");
      setAmount("");
      setDateVal(new Date().toISOString().split("T")[0]);
      await fetchExpenses();
      await fetchBudgetStatus();
    } catch (err) {
      alert("Error saving expense.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteExpense = async (id) => {
    if (!window.confirm("Are you sure you want to delete this transaction?")) return;
    try {
      await API.delete(`/expenses/${id}`);
      await fetchExpenses();
      await fetchBudgetStatus();
    } catch (err) {
      alert("Error deleting record.");
    }
  };

  const handleOpenEdit = (exp) => {
    setEditingExpense(exp);
    setTitle(exp.title);
    setAmount(exp.amount);
    setCategory(exp.category);
    setDateVal(exp.date ? exp.date.split("T")[0] : new Date().toISOString().split("T")[0]);
  };

const handleSetBudget = async (e) => {
    e.preventDefault();
    const limitValue = parseFloat(newBudgetLimit);
    if (isNaN(limitValue) || limitValue <= 0) {
      alert("Please enter a valid amount");
      return;
    }

    const now = new Date();
    const currentMonthInt = now.getMonth() + 1; // 10 for October
    const currentYearInt = now.getFullYear();   // 2026

    try {
      await API.post("/budgets", {
        monthly_limit: limitValue,
        category_id: parseInt(budgetCategory, 10),
        month: currentMonthInt, // Sent as an integer
        year: currentYearInt,
      });
      setShowBudgetModal(false);
      await fetchBudgetStatus();
      alert(`Budget of ₹${limitValue.toLocaleString("en-IN")} set successfully!`);
    } catch (err) {
      console.error("Budget save error:", err.response?.data);
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        alert(detail[0]?.msg || "Validation error");
      } else {
        alert(detail || "Failed to update budget.");
      }
    }
  };

  const totalSpent = expenses.reduce((acc, curr) => acc + parseFloat(curr.amount || 0), 0);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 md:p-8">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-6 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-2">
            <TrendingUp className="text-emerald-500 w-8 h-8" />
            FinPulse Enterprise
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Spend Intelligence, Policy Governance & Financial Analytics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => exportExpensesToCSV(expenses)}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-sm font-medium transition"
          >
            <Download className="w-4 h-4 text-emerald-400" /> Export CSV
          </button>
          <button
            onClick={onLogout}
            className="flex items-center gap-2 px-4 py-2 bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 border border-rose-500/20 rounded-lg text-sm font-medium transition"
          >
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </header>

      {/* Metric Cards & Budget Progress */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800/80 border border-slate-700/80 p-5 rounded-2xl shadow-sm">
          <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Total Outflow</span>
          <p className="text-3xl font-bold text-white mt-2">
            ₹{totalSpent.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </p>
          <span className="text-xs text-slate-500 mt-1 block">{totalRecords} logged transactions</span>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 p-5 rounded-2xl shadow-sm md:col-span-2 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-2">
            <div>
              <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">
                Monthly Spending Ceiling
              </span>
              <p className="text-xl font-bold text-white mt-1">
                {budgetStatus.monthly_limit > 0
                  ? `₹${budgetStatus.actual_spending.toLocaleString("en-IN")} / ₹${budgetStatus.monthly_limit.toLocaleString("en-IN")}`
                  : "No budget cap defined"}
              </p>
            </div>
            <button
              onClick={() => setShowBudgetModal(true)}
              className="text-xs bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 rounded-lg text-white font-medium transition"
            >
              Set Limit
            </button>
          </div>

          {budgetStatus.monthly_limit > 0 && (
            <div>
              <div className="w-full bg-slate-900 rounded-full h-3 overflow-hidden border border-slate-700">
                <div
                  className={`h-full transition-all duration-500 ${
                    budgetStatus.status === "OVERSPENT"
                      ? "bg-rose-500"
                      : budgetStatus.status === "WARNING"
                      ? "bg-amber-400"
                      : "bg-emerald-500"
                  }`}
                  style={{ width: `${Math.min(budgetStatus.percentage_used, 100)}%` }}
                />
              </div>
              <div className="flex justify-between items-center text-xs mt-2">
                <span className="text-slate-400">{budgetStatus.percentage_used}% budget consumed</span>
                {budgetStatus.status === "OVERSPENT" && (
                  <span className="text-rose-400 flex items-center gap-1 font-semibold">
                    <AlertTriangle className="w-3.5 h-3.5" /> Budget Exceeded!
                  </span>
                )}
                {budgetStatus.status === "WARNING" && (
                  <span className="text-amber-400 flex items-center gap-1 font-semibold">
                    <AlertTriangle className="w-3.5 h-3.5" /> 80% Threshold Reached
                  </span>
                )}
                {budgetStatus.status === "SAFE" && (
                  <span className="text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Within Limits
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Analytics Visuals */}
      <div className="mb-8">
        <AnalyticsCharts />
      </div>

      {/* Transaction Management Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Expense Form */}
        <div className="bg-slate-800/80 border border-slate-700/80 p-6 rounded-2xl h-fit">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            {editingExpense ? <Edit3 className="text-amber-400" /> : <PlusCircle className="text-emerald-400" />}
            {editingExpense ? "Edit Transaction" : "Record Expense"}
          </h2>
          <form onSubmit={handleSaveExpense} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. AWS Cloud Services"
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Amount (₹)</label>
              <input
                type="number"
                step="0.01"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="₹ 0.00"
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="Food">Food & Dining</option>
                <option value="Transport">Travel & Transport</option>
                <option value="Utilities">Utilities & Bills</option>
                <option value="Entertainment">Entertainment</option>
                <option value="Software">Software & Cloud</option>
                <option value="Health">Healthcare</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Date</label>
              <input
                type="date"
                required
                value={dateVal}
                onChange={(e) => setDateVal(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold rounded-lg shadow-md transition"
              >
                {loading ? "Processing..." : editingExpense ? "Update Record" : "Save Record"}
              </button>
              {editingExpense && (
                <button
                  type="button"
                  onClick={() => {
                    setEditingExpense(null);
                    setTitle("");
                    setAmount("");
                  }}
                  className="px-4 py-3 bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold rounded-lg transition"
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Transaction Table */}
        <div className="lg:col-span-2 bg-slate-800/80 border border-slate-700/80 p-6 rounded-2xl">
          <h2 className="text-xl font-bold text-white mb-4">Transaction Ledger</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="py-3 px-4 rounded-l-lg">Title</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4 text-right rounded-r-lg">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {expenses.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="text-center py-8 text-slate-500">
                      No transactions recorded yet.
                    </td>
                  </tr>
                ) : (
                  expenses.map((exp) => (
                    <tr key={exp.id} className="hover:bg-slate-700/30 transition">
                      <td className="py-3 px-4 font-medium text-white">{exp.title}</td>
                      <td className="py-3 px-4">
                        <span className="px-2.5 py-1 bg-slate-900 border border-slate-700 rounded-full text-xs text-slate-300">
                          {exp.category}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400">
                        {exp.date ? exp.date.split("T")[0] : "N/A"}
                      </td>
                      <td className="py-3 px-4 font-semibold text-emerald-400">
                        ₹{parseFloat(exp.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => handleOpenEdit(exp)}
                            className="p-1.5 text-slate-400 hover:text-amber-400 transition"
                            title="Edit"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteExpense(exp.id)}
                            className="p-1.5 text-slate-400 hover:text-rose-400 transition"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Budget Set Modal */}
      {showBudgetModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-sm w-full shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1">Set Monthly Spending Ceiling</h3>
            <p className="text-slate-400 text-xs mb-4">
              Category aur monthly limit define karein. Threshold reach hone par progress bar alert show karega.
            </p>
            <form onSubmit={handleSetBudget} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Target Category</label>
                <select
                  value={budgetCategory}
                  onChange={(e) => setBudgetCategory(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="1">Food & Dining</option>
                  <option value="2">Travel & Transport</option>
                  <option value="3">Utilities & Bills</option>
                  <option value="4">Entertainment</option>
                  <option value="5">Software & Cloud</option>
                  <option value="6">Healthcare</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Monthly Limit (₹)</label>
                <input
                  type="number"
                  step="100"
                  required
                  value={newBudgetLimit}
                  onChange={(e) => setNewBudgetLimit(e.target.value)}
                  placeholder="e.g. 2000"
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg text-sm transition"
                >
                  Save Limit
                </button>
                <button
                  type="button"
                  onClick={() => setShowBudgetModal(false)}
                  className="px-4 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-300 font-medium rounded-lg text-sm transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}