"""FinanceWorker 2.0 - Elite Financial Management & Operations"""

from typing import Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from .base import BaseWorker


class FinanceWorker(BaseWorker):
    """Elite Finance Professional for financial operations"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "FinanceWorker"
        self.version = "2.0"
        self.specialties = ["Invoicing", "Payments", "Expenses", "Reporting", "Budgeting"]
        
        self.metrics = {
            "invoices_created": 0, "total_revenue": 0.0, "total_expenses": 0.0,
            "cash_flow": 0.0, "runway_months": 12.0
        }
        
        self.system_prompt = "You are a world-class Finance Professional managing financial operations and strategy."

    async def create_invoice(self, customer: Dict[str, Any], line_items: list) -> Dict[str, Any]:
        """Create professional invoice"""
        total = sum(item.get('amount', 0) * item.get('quantity', 1) for item in line_items)
        invoice = {
            "invoice_id": f"INV-{datetime.now().strftime('%Y%m%d')}-{self.metrics['invoices_created'] + 1}",
            "customer": customer, "line_items": line_items, "total": total,
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "sent"
        }
        filepath = Path("invoices") / f"{invoice['invoice_id']}.json"
        filepath.parent.mkdir(exist_ok=True)
        with open(filepath, 'w') as f:
            import json
            json.dump(invoice, f, indent=2)
        self.metrics["invoices_created"] += 1
        return {"status": "success", "invoice": invoice, "filepath": str(filepath)}

    async def track_expense(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track business expense"""
        expense = {
            "id": f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "vendor": expense_data.get("vendor", "Unknown"),
            "amount": expense_data.get("amount", 0),
            "category": expense_data.get("category", "General"),
            "date": datetime.now().isoformat()
        }
        self.metrics["total_expenses"] += expense["amount"]
        self.metrics["cash_flow"] = self.metrics["total_revenue"] - self.metrics["total_expenses"]
        return {"status": "success", "expense": expense}

    async def generate_report(self, report_type: str = "profit_loss") -> Dict[str, Any]:
        """Generate financial report"""
        report = {
            "type": report_type,
            "revenue": self.metrics["total_revenue"],
            "expenses": self.metrics["total_expenses"],
            "profit": self.metrics["total_revenue"] - self.metrics["total_expenses"],
            "generated": datetime.now().isoformat()
        }
        return {"status": "success", "report": report}

    async def get_metrics(self) -> Dict[str, Any]:
        return {**self.metrics, "worker": self.name, "timestamp": datetime.now().isoformat()}
