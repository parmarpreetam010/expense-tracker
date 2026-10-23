import { useState, useEffect } from "react";
import { PlusCircle, Trash2, IndianRupee, Receipt, LogOut } from "lucide-react";
import API from "../services/api";
import AnalyticsCharts from "./AnalyticsCharts";

const CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Entertainment", "Other"];

export default function Dashboard({ userEmail, onLogout }) {
  const [expenses, setExpenses] = useState([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  // New Expense Form State
  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("Food");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchExpenses = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await API.get("/expenses?limit=100&offset=0");
      setExpenses(res.data.data || []);
      setTotalRecords(res.data.total_records || 0);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load expenses.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExpenses();
  }, []);

  const handleCreateExpense = async (e) => {
    e.preventDefault();
    if (!title || !amount) return;

    setSubmitting(true);
    try {
      await API.post("/expenses", {
        title,
        amount: parseFloat(amount),
        category,
      });
      setTitle("");
      setAmount("");
      setCategory("Food");
      setIsModalOpen(false);
      await fetchExpenses();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add expense.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteExpense = async (id) => {
    if (!window.confirm("Are you sure you want to delete this expense?")) return;
    try {
      await API.delete(`/expenses/${id}`);
      await fetchExpenses();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete expense.");
    }
  };

  const totalSpent = expenses.reduce((acc, curr) => acc + Number(curr.amount || 0), 0);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Expense Tracker</h1>
            <p className="text-slate-400 text-sm mt-1">
              Signed in as <span className="text-emerald-400 font-medium">{userEmail}</span>
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium shadow-md transition"
            >
              <PlusCircle className="w-5 h-5" />
              Add Expense
            </button>
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-medium border border-slate-700 transition"
            >
              <LogOut className="w-4 h-4" />
              Log Out
            </button>
          </div>
        </header>

        {/* Global Error Banner */}
        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-sm">
            {error}
          </div>
        )}

        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl">
              <IndianRupee className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-400">Total Spent</p>
              <h3 className="text-2xl font-bold text-white">₹{totalSpent.toFixed(2)}</h3>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex items-center gap-4">
            <div className="p-3 bg-sky-500/10 text-sky-400 rounded-xl">
              <Receipt className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-400">Total Records</p>
              <h3 className="text-2xl font-bold text-white">{totalRecords}</h3>
            </div>
          </div>
        </div>

        {/* Analytics Section */}
        <AnalyticsCharts expenses={expenses} />

        {/* Expenses Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-6 border-b border-slate-800">
            <h2 className="text-lg font-semibold text-white">Recent Transactions</h2>
          </div>

          {loading ? (
            <div className="p-12 text-center text-slate-400">Loading your transactions...</div>
          ) : expenses.length === 0 ? (
            <div className="p-12 text-center text-slate-400">
              No transactions recorded yet. Click <strong>Add Expense</strong> to start tracking.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/50 text-slate-400 uppercase text-xs">
                  <tr>
                    <th className="py-3 px-6">Title</th>
                    <th className="py-3 px-6">Category</th>
                    <th className="py-3 px-6">Date</th>
                    <th className="py-3 px-6">Amount</th>
                    <th className="py-3 px-6 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {expenses.map((expense) => (
                    <tr key={expense.id} className="hover:bg-slate-800/30 transition">
                      <td className="py-4 px-6 font-medium text-white">{expense.title}</td>
                      <td className="py-4 px-6">
                        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 border border-slate-700 text-slate-300">
                          {expense.category}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-slate-400">
                        {expense.date ? new Date(expense.date).toLocaleDateString() : "N/A"}
                      </td>
                      <td className="py-4 px-6 font-semibold text-emerald-400">
                        ₹{Number(expense.amount).toFixed(2)}
                      </td>
                      <td className="py-4 px-6 text-right">
                        <button
                          onClick={() => handleDeleteExpense(expense.id)}
                          className="p-2 text-slate-400 hover:text-rose-400 transition"
                          title="Delete Expense"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Add Expense Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4">Add New Expense</h3>
            <form onSubmit={handleCreateExpense} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Grocery shopping"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  placeholder="0.00"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2.5 text-slate-400 hover:text-white transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-lg font-medium transition"
                >
                  {submitting ? "Saving..." : "Save Expense"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}