export function exportExpensesToCSV(expenses, filename = "Expense_Report.csv") {
  if (!expenses || expenses.length === 0) return;

  const headers = ["ID", "Title", "Amount (INR)", "Category", "Date"];
  const rows = expenses.map((exp) => [
    exp.id,
    `"${exp.title.replace(/"/g, '""')}"`,
    exp.amount,
    `"${exp.category}"`,
    exp.date || "N/A",
  ]);

  const csvContent =
    "data:text/csv;charset=utf-8," +
    [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}