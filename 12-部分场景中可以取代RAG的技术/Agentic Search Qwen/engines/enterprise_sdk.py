from __future__ import annotations
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
import random

CURRENT_YEAR = datetime.now().year


def _y(date_str: str) -> str:
    """将日期字符串中的年份替换为当前年份"""
    if not date_str:
        return date_str
    parts = date_str.split("-")
    if len(parts) >= 1 and parts[0].isdigit():
        parts[0] = str(CURRENT_YEAR)
    return "-".join(parts)


def _normalize_date(date_str: str) -> str:
    """标准化日期格式为 YYYY-MM-DD，兼容 2026-1-1 -> 2026-01-01"""
    if not date_str or not isinstance(date_str, str):
        return date_str or ""
    parts = date_str.strip().split("-")
    if len(parts) == 3:
        return f"{parts[0].zfill(4)}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
    return date_str


def _normalize_payment_type(type_str: str) -> str:
    """将中文同义词映射为标准类型"""
    if not type_str:
        return type_str
    type_str = type_str.strip()
    income_synonyms = {"收入", "收款", "进账", "应收账款", "营收"}
    expense_synonyms = {"支出", "付款", "出账", "支付", "应付账款", "费用"}
    if type_str in income_synonyms:
        return "收入"
    if type_str in expense_synonyms:
        return "支出"
    return type_str


class EnterpriseSDK:
    def __init__(self):
        self._init_mock_data()

    def _init_mock_data(self):
        self.hr_system = {
            "employees": {
                "E001": {"name": "张伟", "department": "技术部", "position": "高级工程师", "email": "zhangwei@company.com", "phone": "138-0001-0001", "hire_date": "2019-03-15", "status": "在职"},
                "E002": {"name": "李娜", "department": "产品部", "position": "产品经理", "email": "lina@company.com", "phone": "138-0001-0002", "hire_date": "2020-06-01", "status": "在职"},
                "E003": {"name": "王强", "department": "技术部", "position": "架构师", "email": "wangqiang@company.com", "phone": "138-0001-0003", "hire_date": "2018-01-10", "status": "在职"},
                "E004": {"name": "赵敏", "department": "市场部", "position": "市场总监", "email": "zhaomin@company.com", "phone": "138-0001-0004", "hire_date": "2017-09-20", "status": "在职"},
                "E005": {"name": "陈晓", "department": "技术部", "position": "前端工程师", "email": "chenxiao@company.com", "phone": "138-0001-0005", "hire_date": "2021-04-12", "status": "在职"},
                "E006": {"name": "刘洋", "department": "财务部", "position": "财务经理", "email": "liuyang@company.com", "phone": "138-0001-0006", "hire_date": "2019-11-05", "status": "在职"},
                "E007": {"name": "孙磊", "department": "技术部", "position": "后端工程师", "email": "sunlei@company.com", "phone": "138-0001-0007", "hire_date": "2022-02-28", "status": "在职"},
                "E008": {"name": "周琳", "department": "人事部", "position": "HR经理", "email": "zhoulin@company.com", "phone": "138-0001-0008", "hire_date": "2018-07-15", "status": "在职"},
            },
            "leave_records": [
                {"employee_id": "E001", "type": "年假", "start": _y("2024-01-15"), "end": _y("2024-01-19"), "status": "已批准"},
                {"employee_id": "E002", "type": "病假", "start": _y("2024-02-10"), "end": _y("2024-02-11"), "status": "已批准"},
                {"employee_id": "E005", "type": "年假", "start": _y("2024-03-01"), "end": _y("2024-03-05"), "status": "待审批"},
            ],
            "org_chart": {
                "CEO": {"name": "黄明", "direct_reports": ["CTO", "CPO", "CMO", "CFO", "CHRO"]},
                "CTO": {"name": "王强", "direct_reports": ["技术部"]},
                "CPO": {"name": "李娜", "direct_reports": ["产品部"]},
                "CMO": {"name": "赵敏", "direct_reports": ["市场部"]},
                "CFO": {"name": "刘洋", "direct_reports": ["财务部"]},
                "CHRO": {"name": "周琳", "direct_reports": ["人事部"]},
            }
        }

        self.finance_system = {
            "budget_" + str(CURRENT_YEAR): {
                "技术部": {"total": 5000000, "spent": 3200000, "remaining": 1800000},
                "产品部": {"total": 2000000, "spent": 1500000, "remaining": 500000},
                "市场部": {"total": 3000000, "spent": 2800000, "remaining": 200000},
                "财务部": {"total": 800000, "spent": 600000, "remaining": 200000},
                "人事部": {"total": 1000000, "spent": 750000, "remaining": 250000},
            },
            "invoices": [
                {"id": f"INV-{CURRENT_YEAR}-001", "client": "星辰科技", "amount": 580000, "status": "已付款", "date": _y("2024-01-15")},
                {"id": f"INV-{CURRENT_YEAR}-002", "client": "云海集团", "amount": 1200000, "status": "待付款", "date": _y("2024-02-20")},
                {"id": f"INV-{CURRENT_YEAR}-003", "client": "蓝桥网络", "amount": 350000, "status": "已付款", "date": _y("2024-03-05")},
                {"id": f"INV-{CURRENT_YEAR}-004", "client": "晨曦数据", "amount": 890000, "status": "逾期", "date": _y("2024-01-30")},
            ],
            "expense_reports": [
                {"id": "EXP-001", "department": "技术部", "category": "云服务", "amount": 450000, "month": _y("2024-01")},
                {"id": "EXP-002", "department": "市场部", "category": "广告投放", "amount": 800000, "month": _y("2024-01")},
                {"id": "EXP-003", "department": "技术部", "category": "设备采购", "amount": 320000, "month": _y("2024-02")},
            ],
            "payments": [
                {"id": f"PAY-{CURRENT_YEAR}-001", "type": "收入", "counterpart": "星辰科技", "amount": 580000, "method": "银行转账", "status": "已完成", "date": _y("2024-01-15"), "description": "云服务技术支持合同首期款", "category": "合同收入"},
                {"id": f"PAY-{CURRENT_YEAR}-002", "type": "支出", "counterpart": "阿里云", "amount": 230000, "method": "银行转账", "status": "已完成", "date": _y("2024-01-20"), "description": "1月云服务器费用", "category": "云服务"},
                {"id": f"PAY-{CURRENT_YEAR}-003", "type": "收入", "counterpart": "蓝桥网络", "amount": 175000, "method": "银行转账", "status": "已完成", "date": _y("2024-02-01"), "description": "网络运维服务半年款", "category": "合同收入"},
                {"id": f"PAY-{CURRENT_YEAR}-004", "type": "支出", "counterpart": "华为技术", "amount": 450000, "method": "银行转账", "status": "已完成", "date": _y("2024-02-10"), "description": "服务器设备采购", "category": "设备采购"},
                {"id": f"PAY-{CURRENT_YEAR}-005", "type": "支出", "counterpart": "字节跳动广告", "amount": 350000, "method": "银行转账", "status": "已完成", "date": _y("2024-02-15"), "description": "Q1线上广告投放", "category": "广告营销"},
                {"id": f"PAY-{CURRENT_YEAR}-006", "type": "收入", "counterpart": "晨曦数据", "amount": 445000, "method": "银行转账", "status": "已完成", "date": _y("2024-02-20"), "description": "数据分析平台首期款", "category": "合同收入"},
                {"id": f"PAY-{CURRENT_YEAR}-007", "type": "支出", "counterpart": "阿里云", "amount": 245000, "method": "银行转账", "status": "已完成", "date": _y("2024-02-20"), "description": "2月云服务器费用", "category": "云服务"},
                {"id": f"PAY-{CURRENT_YEAR}-008", "type": "收入", "counterpart": "星辰科技", "amount": 290000, "method": "银行转账", "status": "已完成", "date": _y("2024-03-01"), "description": "云服务技术支持合同二期款", "category": "合同收入"},
                {"id": f"PAY-{CURRENT_YEAR}-009", "type": "支出", "counterpart": "腾讯云", "amount": 180000, "method": "银行转账", "status": "已完成", "date": _y("2024-03-05"), "description": "CDN加速服务费", "category": "云服务"},
                {"id": f"PAY-{CURRENT_YEAR}-010", "type": "支出", "counterpart": "万得信息", "amount": 120000, "method": "银行转账", "status": "已完成", "date": _y("2024-03-10"), "description": "金融数据接口年费", "category": "数据服务"},
                {"id": f"PAY-{CURRENT_YEAR}-011", "type": "收入", "counterpart": "蓝桥网络", "amount": 175000, "method": "银行转账", "status": "待到账", "date": _y("2024-03-15"), "description": "网络运维服务尾款", "category": "合同收入"},
                {"id": f"PAY-{CURRENT_YEAR}-012", "type": "支出", "counterpart": "阿里云", "amount": 260000, "method": "银行转账", "status": "已完成", "date": _y("2024-03-20"), "description": "3月云服务器费用", "category": "云服务"},
                {"id": f"PAY-{CURRENT_YEAR}-013", "type": "收入", "counterpart": "星辰科技", "amount": 320000, "method": "银行转账", "status": "已完成", "date": _y("2024-05-12"), "description": "云服务技术支持合同尾款", "category": "合同收入"},
                {"id": f"PAY-{CURRENT_YEAR}-014", "type": "支出", "counterpart": "阿里云", "amount": 275000, "method": "银行转账", "status": "已完成", "date": _y("2024-05-13"), "description": "5月云服务器费用", "category": "云服务"},
                {"id": f"PAY-{CURRENT_YEAR}-015", "type": "收入", "counterpart": "云海集团", "amount": 600000, "method": "银行转账", "status": "已完成", "date": _y("2024-05-14"), "description": "数据中台项目首期款", "category": "合同收入"},
                {"id": f"PAY-{CURRENT_YEAR}-016", "type": "支出", "counterpart": "腾讯广告", "amount": 180000, "method": "银行转账", "status": "已完成", "date": _y("2024-05-15"), "description": "5月线上广告投放", "category": "广告营销"},
                {"id": f"PAY-{CURRENT_YEAR}-017", "type": "支出", "counterpart": "京东云", "amount": 150000, "method": "银行转账", "status": "待付款", "date": _y("2024-05-16"), "description": "对象存储服务费", "category": "云服务"},
                {"id": f"PAY-{CURRENT_YEAR}-018", "type": "收入", "counterpart": "晨曦数据", "amount": 445000, "method": "银行转账", "status": "已完成", "date": _y("2024-05-17"), "description": "数据分析平台二期款", "category": "合同收入"},
            ],
            "transactions": [
                {"id": f"TXN-{CURRENT_YEAR}-001", "type": "收入", "amount": 580000, "date": _y("2024-01-15"), "counterpart": "星辰科技", "account": "工商银行-基本户", "description": "合同收款"},
                {"id": f"TXN-{CURRENT_YEAR}-002", "type": "支出", "amount": 230000, "date": _y("2024-01-20"), "counterpart": "阿里云", "account": "工商银行-基本户", "description": "云服务费"},
                {"id": f"TXN-{CURRENT_YEAR}-003", "type": "收入", "amount": 175000, "date": _y("2024-02-01"), "counterpart": "蓝桥网络", "account": "工商银行-基本户", "description": "服务收款"},
                {"id": f"TXN-{CURRENT_YEAR}-004", "type": "支出", "amount": 450000, "date": _y("2024-02-10"), "counterpart": "华为技术", "account": "建设银行-一般户", "description": "设备采购"},
                {"id": f"TXN-{CURRENT_YEAR}-005", "type": "支出", "amount": 350000, "date": _y("2024-02-15"), "counterpart": "字节跳动广告", "account": "工商银行-基本户", "description": "广告投放"},
                {"id": f"TXN-{CURRENT_YEAR}-006", "type": "收入", "amount": 445000, "date": _y("2024-02-20"), "counterpart": "晨曦数据", "account": "工商银行-基本户", "description": "平台首期款"},
                {"id": f"TXN-{CURRENT_YEAR}-007", "type": "支出", "amount": 245000, "date": _y("2024-02-20"), "counterpart": "阿里云", "account": "工商银行-基本户", "description": "云服务费"},
                {"id": f"TXN-{CURRENT_YEAR}-008", "type": "收入", "amount": 290000, "date": _y("2024-03-01"), "counterpart": "星辰科技", "account": "工商银行-基本户", "description": "合同二期款"},
                {"id": f"TXN-{CURRENT_YEAR}-009", "type": "支出", "amount": 180000, "date": _y("2024-03-05"), "counterpart": "腾讯云", "account": "工商银行-基本户", "description": "CDN服务费"},
                {"id": f"TXN-{CURRENT_YEAR}-010", "type": "支出", "amount": 120000, "date": _y("2024-03-10"), "counterpart": "万得信息", "account": "建设银行-一般户", "description": "数据接口费"},
                {"id": f"TXN-{CURRENT_YEAR}-011", "type": "收入", "amount": 175000, "date": _y("2024-03-15"), "counterpart": "蓝桥网络", "account": "工商银行-基本户", "description": "服务尾款"},
                {"id": f"TXN-{CURRENT_YEAR}-012", "type": "支出", "amount": 260000, "date": _y("2024-03-20"), "counterpart": "阿里云", "account": "工商银行-基本户", "description": "云服务费"},
                {"id": f"TXN-{CURRENT_YEAR}-013", "type": "收入", "amount": 320000, "date": _y("2024-05-12"), "counterpart": "星辰科技", "account": "工商银行-基本户", "description": "合同尾款"},
                {"id": f"TXN-{CURRENT_YEAR}-014", "type": "支出", "amount": 275000, "date": _y("2024-05-13"), "counterpart": "阿里云", "account": "工商银行-基本户", "description": "5月云服务费"},
                {"id": f"TXN-{CURRENT_YEAR}-015", "type": "收入", "amount": 600000, "date": _y("2024-05-14"), "counterpart": "云海集团", "account": "工商银行-基本户", "description": "数据中台首期款"},
                {"id": f"TXN-{CURRENT_YEAR}-016", "type": "支出", "amount": 180000, "date": _y("2024-05-15"), "counterpart": "腾讯广告", "account": "工商银行-基本户", "description": "5月广告费"},
                {"id": f"TXN-{CURRENT_YEAR}-017", "type": "支出", "amount": 150000, "date": _y("2024-05-16"), "counterpart": "京东云", "account": "建设银行-一般户", "description": "对象存储费"},
                {"id": f"TXN-{CURRENT_YEAR}-018", "type": "收入", "amount": 445000, "date": _y("2024-05-17"), "counterpart": "晨曦数据", "account": "工商银行-基本户", "description": "平台二期款"},
            ],
        }

        self.project_system = {
            "projects": {
                "P001": {"name": "智能客服系统V2", "status": "进行中", "lead": "E003", "department": "技术部", "start": _y("2024-01-01"), "deadline": _y("2024-06-30"), "progress": 65, "priority": "高"},
                "P002": {"name": "数据中台建设", "status": "进行中", "lead": "E001", "department": "技术部", "start": _y("2024-02-15"), "deadline": _y("2024-09-30"), "progress": 30, "priority": "高"},
                "P003": {"name": "移动端App改版", "status": "规划中", "lead": "E002", "department": "产品部", "start": _y("2024-04-01"), "deadline": _y("2024-08-31"), "progress": 0, "priority": "中"},
                "P004": {"name": "品牌升级项目", "status": "已完成", "lead": "E004", "department": "市场部", "start": _y("2023-10-01"), "deadline": _y("2024-03-31"), "progress": 100, "priority": "中"},
                "P005": {"name": "安全合规审计", "status": "进行中", "lead": "E003", "department": "技术部", "start": _y("2024-03-01"), "deadline": _y("2024-05-31"), "progress": 80, "priority": "高"},
            },
            "milestones": [
                {"project_id": "P001", "name": "需求分析完成", "date": _y("2024-02-01"), "status": "已完成"},
                {"project_id": "P001", "name": "核心模块开发", "date": _y("2024-04-15"), "status": "进行中"},
                {"project_id": "P002", "name": "架构设计评审", "date": _y("2024-03-15"), "status": "已完成"},
                {"project_id": "P002", "name": "数据管道搭建", "date": _y("2024-05-30"), "status": "进行中"},
            ]
        }

        self.wiki_system = {
            "policies": [
                {"title": "远程办公政策", "content": "公司允许员工每周最多2天远程办公。需要提前一天在OA系统中申请，经直属上级批准后生效。远程办公期间需保持在线状态，及时响应工作沟通。", "category": "人事政策", "updated": _y("2024-01-10")},
                {"title": "报销流程规范", "content": "所有报销需在费用发生后30天内提交。单笔超过5000元需部门经理审批。差旅费标准：一线城市住宿不超过600元/晚，二线城市不超过400元/晚。", "category": "财务政策", "updated": _y("2024-02-05")},
                {"title": "代码审查规范", "content": "所有代码合并到主分支前必须经过至少2人审查。关键模块需要架构师审查。审查重点包括：代码质量、安全性、性能、可维护性。", "category": "技术规范", "updated": _y("2024-03-12")},
                {"title": "新员工入职流程", "content": "新员工入职需完成：1.人事部报到登记 2.IT设备领取与账号开通 3.部门入职培训 4.导师分配 5.试用期目标设定。试用期为3-6个月。", "category": "人事政策", "updated": _y("2024-01-20")},
                {"title": "数据安全管理制度", "content": "所有生产数据访问需通过VPN连接。敏感数据（用户信息、财务数据）需加密存储。数据导出需经数据安全委员会审批。违规者将按严重程度给予警告至解除劳动合同的处罚。", "category": "安全政策", "updated": _y("2024-03-01")},
            ],
            "tech_docs": [
                {"title": "微服务架构设计指南", "content": "本指南描述了公司微服务架构的设计原则和实践。服务间通信使用gRPC，服务发现使用Consul，API网关使用Kong。每个服务独立部署，独立数据库。", "category": "架构文档", "updated": _y("2024-02-20")},
                {"title": "CI/CD流水线配置", "content": "代码提交触发Jenkins构建，单元测试覆盖率需达到80%以上。构建成功后自动部署到staging环境，经QA验证后手动触发生产部署。生产部署窗口：工作日10:00-16:00。", "category": "运维文档", "updated": _y("2024-03-05")},
                {"title": "API设计规范", "content": "RESTful API设计遵循以下原则：URL使用小写和连字符，使用HTTP方法表示操作，返回标准HTTP状态码，分页使用cursor-based方式，版本号放在URL中（/v1/）。", "category": "技术规范", "updated": _y("2024-01-25")},
            ]
        }

    def call_hr_system(self, action: str, params: dict = None) -> str:
        if params is None:
            params = {}

        if action == "get_employee":
            emp_id = params.get("employee_id")
            if emp_id and emp_id in self.hr_system["employees"]:
                return json.dumps({
                    "system": "HR",
                    "action": "get_employee",
                    "data": self.hr_system["employees"][emp_id]
                }, ensure_ascii=False, indent=2)
            return json.dumps({"system": "HR", "action": "get_employee", "data": None, "message": "Employee not found"}, ensure_ascii=False)

        elif action == "search_employees":
            keyword = params.get("keyword", "").lower()
            results = []
            for emp_id, emp in self.hr_system["employees"].items():
                if keyword in json.dumps(emp, ensure_ascii=False).lower():
                    results.append({"id": emp_id, **emp})
            return json.dumps({
                "system": "HR",
                "action": "search_employees",
                "data": results
            }, ensure_ascii=False, indent=2)

        elif action == "get_leave_records":
            emp_id = params.get("employee_id")
            records = self.hr_system["leave_records"]
            if emp_id:
                records = [r for r in records if r["employee_id"] == emp_id]
            return json.dumps({
                "system": "HR",
                "action": "get_leave_records",
                "data": records
            }, ensure_ascii=False, indent=2)

        elif action == "get_org_chart":
            return json.dumps({
                "system": "HR",
                "action": "get_org_chart",
                "data": self.hr_system["org_chart"]
            }, ensure_ascii=False, indent=2)

        else:
            return json.dumps({"system": "HR", "error": f"Unknown action: {action}"}, ensure_ascii=False)

    def call_finance_system(self, action: str, params: dict = None) -> str:
        if params is None:
            params = {}

        if action == "get_budget":
            budget_key = f"budget_{CURRENT_YEAR}"
            department = params.get("department")
            if department and department in self.finance_system.get(budget_key, {}):
                return json.dumps({
                    "system": "Finance",
                    "action": "get_budget",
                    "data": {department: self.finance_system[budget_key][department]}
                }, ensure_ascii=False, indent=2)
            return json.dumps({
                "system": "Finance",
                "action": "get_budget",
                "data": self.finance_system.get(budget_key, {})
            }, ensure_ascii=False, indent=2)

        elif action == "get_invoices":
            status = params.get("status")
            start_date = _normalize_date(params.get("start_date", ""))
            end_date = _normalize_date(params.get("end_date", ""))
            invoices = self.finance_system["invoices"]
            if status:
                invoices = [inv for inv in invoices if inv["status"] == status]
            if start_date:
                invoices = [inv for inv in invoices if inv["date"] >= start_date]
            if end_date:
                invoices = [inv for inv in invoices if inv["date"] <= end_date]
            return json.dumps({
                "system": "Finance",
                "action": "get_invoices",
                "data": invoices
            }, ensure_ascii=False, indent=2)

        elif action == "get_expenses":
            department = params.get("department")
            start_date = _normalize_date(params.get("start_date", ""))
            end_date = _normalize_date(params.get("end_date", ""))
            expenses = self.finance_system["expense_reports"]
            if department:
                expenses = [e for e in expenses if e["department"] == department]
            if start_date:
                expenses = [e for e in expenses if e["date"] >= start_date]
            if end_date:
                expenses = [e for e in expenses if e["date"] <= end_date]
            return json.dumps({
                "system": "Finance",
                "action": "get_expenses",
                "data": expenses
            }, ensure_ascii=False, indent=2)

        elif action == "get_payments":
            payment_type = _normalize_payment_type(params.get("type", ""))
            status = params.get("status")
            start_date = _normalize_date(params.get("start_date", ""))
            end_date = _normalize_date(params.get("end_date", ""))
            category = params.get("category")
            payments = self.finance_system["payments"]
            if payment_type:
                payments = [p for p in payments if p["type"] == payment_type]
            if status:
                payments = [p for p in payments if p["status"] == status]
            if start_date:
                payments = [p for p in payments if p["date"] >= start_date]
            if end_date:
                payments = [p for p in payments if p["date"] <= end_date]
            if category:
                payments = [p for p in payments if category in p.get("category", "")]
            total_income = sum(p["amount"] for p in payments if p["type"] == "收入")
            total_expense = sum(p["amount"] for p in payments if p["type"] == "支出")
            return json.dumps({
                "system": "Finance",
                "action": "get_payments",
                "summary": {
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "net_amount": total_income - total_expense,
                    "count": len(payments)
                },
                "data": payments
            }, ensure_ascii=False, indent=2)

        elif action == "get_transactions":
            txn_type = _normalize_payment_type(params.get("type", ""))
            start_date = _normalize_date(params.get("start_date", ""))
            end_date = _normalize_date(params.get("end_date", ""))
            account = params.get("account")
            transactions = self.finance_system["transactions"]
            if txn_type:
                transactions = [t for t in transactions if t["type"] == txn_type]
            if start_date:
                transactions = [t for t in transactions if t["date"] >= start_date]
            if end_date:
                transactions = [t for t in transactions if t["date"] <= end_date]
            if account:
                transactions = [t for t in transactions if account in t.get("account", "")]
            total_income = sum(t["amount"] for t in transactions if t["type"] == "收入")
            total_expense = sum(t["amount"] for t in transactions if t["type"] == "支出")
            return json.dumps({
                "system": "Finance",
                "action": "get_transactions",
                "summary": {
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "net_amount": total_income - total_expense,
                    "count": len(transactions)
                },
                "data": transactions
            }, ensure_ascii=False, indent=2)

        else:
            return json.dumps({"system": "Finance", "error": f"Unknown action: {action}"}, ensure_ascii=False)

    def call_project_system(self, action: str, params: dict = None) -> str:
        if params is None:
            params = {}

        if action == "get_project":
            project_id = params.get("project_id")
            if project_id and project_id in self.project_system["projects"]:
                return json.dumps({
                    "system": "Project",
                    "action": "get_project",
                    "data": {"id": project_id, **self.project_system["projects"][project_id]}
                }, ensure_ascii=False, indent=2)
            return json.dumps({"system": "Project", "action": "get_project", "data": None, "message": "Project not found"}, ensure_ascii=False)

        elif action == "search_projects":
            keyword = params.get("keyword", "").lower()
            status = params.get("status")
            results = []
            for pid, proj in self.project_system["projects"].items():
                if status and proj["status"] != status:
                    continue
                if keyword and keyword not in json.dumps(proj, ensure_ascii=False).lower():
                    continue
                results.append({"id": pid, **proj})
            return json.dumps({
                "system": "Project",
                "action": "search_projects",
                "data": results
            }, ensure_ascii=False, indent=2)

        elif action == "get_milestones":
            project_id = params.get("project_id")
            milestones = self.project_system["milestones"]
            if project_id:
                milestones = [m for m in milestones if m["project_id"] == project_id]
            return json.dumps({
                "system": "Project",
                "action": "get_milestones",
                "data": milestones
            }, ensure_ascii=False, indent=2)

        else:
            return json.dumps({"system": "Project", "error": f"Unknown action: {action}"}, ensure_ascii=False)

    def call_wiki_system(self, action: str, params: dict = None) -> str:
        if params is None:
            params = {}

        if action == "search_policies":
            keyword = params.get("keyword", "").lower()
            category = params.get("category")
            results = []
            for p in self.wiki_system["policies"]:
                if category and p["category"] != category:
                    continue
                if keyword and keyword not in json.dumps(p, ensure_ascii=False).lower():
                    continue
                results.append(p)
            return json.dumps({
                "system": "Wiki",
                "action": "search_policies",
                "data": results
            }, ensure_ascii=False, indent=2)

        elif action == "search_tech_docs":
            keyword = params.get("keyword", "").lower()
            category = params.get("category")
            results = []
            for d in self.wiki_system["tech_docs"]:
                if category and d["category"] != category:
                    continue
                if keyword and keyword not in json.dumps(d, ensure_ascii=False).lower():
                    continue
                results.append(d)
            return json.dumps({
                "system": "Wiki",
                "action": "search_tech_docs",
                "data": results
            }, ensure_ascii=False, indent=2)

        elif action == "get_all_categories":
            categories = set()
            for p in self.wiki_system["policies"]:
                categories.add(p["category"])
            for d in self.wiki_system["tech_docs"]:
                categories.add(d["category"])
            return json.dumps({
                "system": "Wiki",
                "action": "get_all_categories",
                "data": list(categories)
            }, ensure_ascii=False, indent=2)

        else:
            return json.dumps({"system": "Wiki", "error": f"Unknown action: {action}"}, ensure_ascii=False)

    def call(self, system: str, action: str, params: dict = None) -> str:
        if system == "hr":
            return self.call_hr_system(action, params)
        elif system == "finance":
            return self.call_finance_system(action, params)
        elif system == "project":
            return self.call_project_system(action, params)
        elif system == "wiki":
            return self.call_wiki_system(action, params)
        else:
            return json.dumps({"error": f"Unknown system: {system}. Available: hr, finance, project, wiki"}, ensure_ascii=False)

    def get_available_systems(self) -> str:
        return json.dumps({
            "hr": {
                "description": "人力资源系统",
                "actions": [
                    {"name": "get_employee", "params": ["employee_id"], "description": "获取员工信息"},
                    {"name": "search_employees", "params": ["keyword"], "description": "搜索员工"},
                    {"name": "get_leave_records", "params": ["employee_id(可选)"], "description": "获取请假记录"},
                    {"name": "get_org_chart", "params": [], "description": "获取组织架构"},
                ]
            },
            "finance": {
                "description": "财务系统",
                "actions": [
                    {"name": "get_budget", "params": ["department(可选)"], "description": "获取预算信息"},
                    {"name": "get_invoices", "params": ["status(可选)"], "description": "获取发票信息"},
                    {"name": "get_expenses", "params": ["department(可选)"], "description": "获取费用报表"},
                    {"name": "get_payments", "params": ["type(可选:收入/支出)", "status(可选)", "start_date(可选)", "end_date(可选)", "category(可选)"], "description": "获取支付流水数据，支持按类型、状态、日期范围、分类筛选，返回汇总信息"},
                    {"name": "get_transactions", "params": ["type(可选:收入/支出)", "start_date(可选)", "end_date(可选)", "account(可选)"], "description": "获取交易流水数据，支持按类型、日期范围、账户筛选，返回汇总信息"},
                ]
            },
            "project": {
                "description": "项目管理系统",
                "actions": [
                    {"name": "get_project", "params": ["project_id"], "description": "获取项目信息"},
                    {"name": "search_projects", "params": ["keyword", "status(可选)"], "description": "搜索项目"},
                    {"name": "get_milestones", "params": ["project_id(可选)"], "description": "获取项目里程碑"},
                ]
            },
            "wiki": {
                "description": "企业知识库",
                "actions": [
                    {"name": "search_policies", "params": ["keyword", "category(可选)"], "description": "搜索公司政策"},
                    {"name": "search_tech_docs", "params": ["keyword", "category(可选)"], "description": "搜索技术文档"},
                    {"name": "get_all_categories", "params": [], "description": "获取所有文档分类"},
                ]
            }
        }, ensure_ascii=False, indent=2)
