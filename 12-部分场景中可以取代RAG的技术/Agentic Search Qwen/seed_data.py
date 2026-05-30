from __future__ import annotations
from engines.database import DatabaseEngine
from engines.vector_db import VectorDBEngine
from engines.keyword_search import KeywordSearchEngine
from config import CODE_REPO_DIR
import os


def seed_database(db: DatabaseEngine):
    db.init_tables()

    employees = [
        {"name": "张伟", "department": "技术部", "position": "高级工程师", "email": "zhangwei@company.com", "phone": "138-0001-0001", "hire_date": "2019-03-15", "salary": 35000, "status": "active"},
        {"name": "李娜", "department": "产品部", "position": "产品经理", "email": "lina@company.com", "phone": "138-0001-0002", "hire_date": "2020-06-01", "salary": 30000, "status": "active"},
        {"name": "王强", "department": "技术部", "position": "架构师", "email": "wangqiang@company.com", "phone": "138-0001-0003", "hire_date": "2018-01-10", "salary": 50000, "status": "active"},
        {"name": "赵敏", "department": "市场部", "position": "市场总监", "email": "zhaomin@company.com", "phone": "138-0001-0004", "hire_date": "2017-09-20", "salary": 45000, "status": "active"},
        {"name": "陈晓", "department": "技术部", "position": "前端工程师", "email": "chenxiao@company.com", "phone": "138-0001-0005", "hire_date": "2021-04-12", "salary": 25000, "status": "active"},
        {"name": "刘洋", "department": "财务部", "position": "财务经理", "email": "liuyang@company.com", "phone": "138-0001-0006", "hire_date": "2019-11-05", "salary": 32000, "status": "active"},
        {"name": "孙磊", "department": "技术部", "position": "后端工程师", "email": "sunlei@company.com", "phone": "138-0001-0007", "hire_date": "2022-02-28", "salary": 28000, "status": "active"},
        {"name": "周琳", "department": "人事部", "position": "HR经理", "email": "zhoulin@company.com", "phone": "138-0001-0008", "hire_date": "2018-07-15", "salary": 30000, "status": "active"},
        {"name": "吴涛", "department": "技术部", "position": "测试工程师", "email": "wutao@company.com", "phone": "138-0001-0009", "hire_date": "2021-08-20", "salary": 22000, "status": "active"},
        {"name": "郑华", "department": "产品部", "position": "产品助理", "email": "zhenghua@company.com", "phone": "138-0001-0010", "hire_date": "2023-01-15", "salary": 18000, "status": "active"},
    ]

    departments = [
        {"name": "技术部", "manager": "王强", "budget": 5000000, "headcount": 25, "location": "A栋3楼"},
        {"name": "产品部", "manager": "李娜", "budget": 2000000, "headcount": 10, "location": "A栋4楼"},
        {"name": "市场部", "manager": "赵敏", "budget": 3000000, "headcount": 15, "location": "B栋2楼"},
        {"name": "财务部", "manager": "刘洋", "budget": 800000, "headcount": 8, "location": "B栋3楼"},
        {"name": "人事部", "manager": "周琳", "budget": 1000000, "headcount": 6, "location": "B栋3楼"},
    ]

    projects = [
        {"name": "智能客服系统V2", "department": "技术部", "lead": "王强", "status": "进行中", "start_date": "2024-01-01", "end_date": "2024-06-30", "budget": 800000, "description": "基于大语言模型的智能客服系统升级，支持多轮对话和知识库问答"},
        {"name": "数据中台建设", "department": "技术部", "lead": "张伟", "status": "进行中", "start_date": "2024-02-15", "end_date": "2024-09-30", "budget": 1200000, "description": "统一数据平台建设，实现数据采集、清洗、存储、分析一体化"},
        {"name": "移动端App改版", "department": "产品部", "lead": "李娜", "status": "规划中", "start_date": "2024-04-01", "end_date": "2024-08-31", "budget": 500000, "description": "移动端应用全面改版，优化用户体验和性能"},
        {"name": "品牌升级项目", "department": "市场部", "lead": "赵敏", "status": "已完成", "start_date": "2023-10-01", "end_date": "2024-03-31", "budget": 600000, "description": "公司品牌视觉体系全面升级，包括logo、VI、官网等"},
        {"name": "安全合规审计", "department": "技术部", "lead": "王强", "status": "进行中", "start_date": "2024-03-01", "end_date": "2024-05-31", "budget": 300000, "description": "信息安全等级保护认证和SOC2合规审计"},
    ]

    contracts = [
        {"client_name": "星辰科技", "type": "服务合同", "amount": 580000, "status": "执行中", "sign_date": "2024-01-15", "expire_date": "2025-01-14", "responsible_person": "赵敏", "description": "云服务技术支持合同"},
        {"client_name": "云海集团", "type": "采购合同", "amount": 1200000, "status": "待签署", "sign_date": "", "expire_date": "", "responsible_person": "刘洋", "description": "服务器设备采购"},
        {"client_name": "蓝桥网络", "type": "服务合同", "amount": 350000, "status": "已完成", "sign_date": "2023-06-01", "expire_date": "2024-05-31", "responsible_person": "赵敏", "description": "网络运维服务"},
        {"client_name": "晨曦数据", "type": "销售合同", "amount": 890000, "status": "逾期", "sign_date": "2023-12-01", "expire_date": "2024-11-30", "responsible_person": "李娜", "description": "数据分析平台销售"},
    ]

    products = [
        {"name": "CloudEngine Pro", "category": "云服务", "price": 9999, "stock": 999, "description": "企业级云服务管理平台，支持多云管理和自动化运维", "launch_date": "2023-06-01"},
        {"name": "DataInsight", "category": "数据分析", "price": 59999, "stock": 999, "description": "智能数据分析平台，支持实时数据流处理和可视化", "launch_date": "2023-09-15"},
        {"name": "SecureShield", "category": "安全", "price": 29999, "stock": 999, "description": "企业安全防护系统，包含WAF、DDoS防护、入侵检测", "launch_date": "2024-01-20"},
        {"name": "SmartChat", "category": "AI", "price": 19999, "stock": 999, "description": "智能客服机器人，基于大语言模型，支持多轮对话", "launch_date": "2024-03-01"},
    ]

    db.insert_data("employees", employees)
    db.insert_data("departments", departments)
    db.insert_data("projects", projects)
    db.insert_data("contracts", contracts)
    db.insert_data("products", products)

    print("✅ SQLite数据库初始化完成")


def seed_vector_db(vector_db: VectorDBEngine):
    company_docs = [
        "公司成立于2015年，总部位于北京，在上海、深圳、成都设有分公司。目前员工总数约300人，年营收超过2亿元。",
        "公司核心技术栈包括：微服务架构（Spring Cloud + Kubernetes）、大数据平台（Flink + Spark）、AI平台（PyTorch + 自研推理引擎）。",
        "2024年公司战略重点：1）AI产品线扩展，推出SmartChat 2.0；2）海外市场拓展，重点布局东南亚；3）数据安全合规，完成SOC2认证。",
        "公司文化价值观：客户第一、技术驱动、开放协作、追求卓越。每季度举办Hackathon，鼓励创新。",
        "公司福利体系：五险一金、补充医疗保险、年度体检、弹性工作制、远程办公（每周最多2天）、年度团建、学习发展基金。",
        "技术部是公司最大的部门，拥有25名工程师，分为前端组、后端组、数据组、AI组和DevOps组。",
        "公司目前有3个核心产品线：CloudEngine（云服务管理）、DataInsight（数据分析）、SecureShield（安全防护）。",
        "2023年公司获得B轮融资2亿元，由红杉资本领投。目前估值约20亿元。",
    ]

    tech_docs = [
        "微服务架构规范：所有新服务必须使用Spring Cloud框架，服务间通信使用gRPC，API网关使用Kong。每个服务必须有健康检查端点和优雅关闭机制。",
        "数据库规范：生产环境必须使用MySQL 8.0+，读写分离，主从同步。禁止跨库JOIN，大数据量表必须分库分表。所有SQL必须经过审计。",
        "缓存策略：使用Redis集群作为缓存层，热点数据TTL不超过1小时，缓存击穿使用互斥锁防护，缓存雪崩使用随机过期时间。",
        "消息队列规范：使用Apache Kafka作为消息中间件，消息必须持久化，消费者必须实现幂等性，死信队列必须有监控告警。",
        "日志规范：使用ELK（Elasticsearch + Logstash + Kibana）作为日志平台。日志级别：DEBUG/INFO/WARN/ERROR。生产环境默认INFO级别。",
        "CI/CD流程：代码提交触发Jenkins构建，单元测试覆盖率≥80%，SonarQube质量门禁通过后自动部署到staging，QA验证后手动触发生产部署。",
        "安全开发规范：所有API必须鉴权，敏感数据必须加密，SQL必须参数化，XSS/CSRF防护必须开启，依赖库漏洞必须及时修复。",
        "监控告警：使用Prometheus + Grafana监控，所有服务必须暴露metrics端点，P99延迟超过500ms触发告警，错误率超过1%触发告警。",
    ]

    meeting_docs = [
        "2024年Q1技术复盘会议纪要：1）智能客服系统V2进度正常，核心模块开发中；2）数据中台架构设计已通过评审；3）安全合规审计进展顺利，预计5月完成；4）技术债务清理计划已制定。",
        "2024年产品规划会议纪要：1）移动端App改版4月启动；2）SmartChat 2.0计划Q3发布；3）DataInsight将增加实时分析功能；4）SecureShield将增加零信任网络模块。",
        "2024年市场策略会议纪要：1）品牌升级已完成，新VI已上线；2）Q2重点推广SmartChat；3）东南亚市场调研已完成，计划Q3进入；4）年度营销预算300万。",
        "2024年财务预算会议纪要：1）技术部预算500万，重点投入AI和数据中台；2）市场部预算300万，重点投入品牌推广；3）全公司人力成本预算约4000万。",
    ]

    vector_db.add_documents("company_info", company_docs,
                            metadatas=[{"category": "公司概况", "source": "公司介绍"} for _ in company_docs])

    vector_db.add_documents("tech_docs", tech_docs,
                            metadatas=[{"category": "技术规范", "source": "技术文档"} for _ in tech_docs])

    vector_db.add_documents("meeting_notes", meeting_docs,
                            metadatas=[{"category": "会议纪要", "source": "会议记录"} for _ in meeting_docs])

    print("✅ 向量数据库初始化完成")


def seed_keyword_search(keyword_engine: KeywordSearchEngine):
    policies = [
        {"id": "policy_001", "title": "远程办公政策", "content": "公司允许员工每周最多2天远程办公。需要提前一天在OA系统中申请，经直属上级批准后生效。远程办公期间需保持在线状态，及时响应工作沟通。远程办公不适用于试用期员工和需要现场操作的岗位。", "category": "人事政策", "source": "HR部门"},
        {"id": "policy_002", "title": "报销流程规范", "content": "所有报销需在费用发生后30天内提交。单笔超过5000元需部门经理审批。差旅费标准：一线城市住宿不超过600元/晚，二线城市不超过400元/晚。餐饮补贴：一线城市100元/天，二线城市80元/天。", "category": "财务政策", "source": "财务部"},
        {"id": "policy_003", "title": "代码审查规范", "content": "所有代码合并到主分支前必须经过至少2人审查。关键模块需要架构师审查。审查重点包括：代码质量、安全性、性能、可维护性。审查应在24小时内完成。", "category": "技术规范", "source": "技术部"},
        {"id": "policy_004", "title": "新员工入职流程", "content": "新员工入职需完成：1.人事部报到登记 2.IT设备领取与账号开通 3.部门入职培训 4.导师分配 5.试用期目标设定。试用期为3-6个月。入职第一周为适应期，不安排核心任务。", "category": "人事政策", "source": "HR部门"},
        {"id": "policy_005", "title": "数据安全管理制度", "content": "所有生产数据访问需通过VPN连接。敏感数据（用户信息、财务数据）需加密存储。数据导出需经数据安全委员会审批。违规者将按严重程度给予警告至解除劳动合同的处罚。", "category": "安全政策", "source": "安全部"},
        {"id": "policy_006", "title": "加班管理政策", "content": "工作日加班需提前申请，加班费按1.5倍计算。周末加班可调休或按2倍计算。法定节假日加班按3倍计算。每月加班时长不超过36小时。连续加班不超过3天。", "category": "人事政策", "source": "HR部门"},
    ]

    tech_articles = [
        {"id": "tech_001", "title": "微服务架构设计指南", "content": "本指南描述了公司微服务架构的设计原则和实践。服务间通信使用gRPC，服务发现使用Consul，API网关使用Kong。每个服务独立部署，独立数据库。推荐使用Docker容器化部署。", "category": "架构文档", "source": "架构组"},
        {"id": "tech_002", "title": "CI/CD流水线配置", "content": "代码提交触发Jenkins构建，单元测试覆盖率需达到80%以上。构建成功后自动部署到staging环境，经QA验证后手动触发生产部署。生产部署窗口：工作日10:00-16:00。回滚方案必须提前准备。", "category": "运维文档", "source": "DevOps组"},
        {"id": "tech_003", "title": "API设计规范", "content": "RESTful API设计遵循以下原则：URL使用小写和连字符，使用HTTP方法表示操作，返回标准HTTP状态码，分页使用cursor-based方式，版本号放在URL中（/v1/）。错误响应必须包含error code和message。", "category": "技术规范", "source": "架构组"},
        {"id": "tech_004", "title": "Python开发规范", "content": "使用Python 3.10+，代码风格遵循PEP 8，类型注解必须完整，使用Black格式化，isort排序import，mypy类型检查。虚拟环境使用poetry管理依赖。", "category": "技术规范", "source": "AI组"},
        {"id": "tech_005", "title": "前端开发规范", "content": "使用React 18 + TypeScript，状态管理使用Zustand，样式使用Tailwind CSS，组件库使用Ant Design。所有组件必须编写单元测试，使用React Testing Library。", "category": "技术规范", "source": "前端组"},
    ]

    keyword_engine.add_documents("policies", policies)
    keyword_engine.add_documents("tech_articles", tech_articles)

    print("✅ 关键词搜索索引初始化完成")


def seed_code_repo():
    os.makedirs(CODE_REPO_DIR, exist_ok=True)

    src_dir = os.path.join(CODE_REPO_DIR, "src")
    os.makedirs(src_dir, exist_ok=True)

    with open(os.path.join(src_dir, "main.py"), "w", encoding="utf-8") as f:
        f.write('''"""主应用程序入口"""
from fastapi import FastAPI
from routers import api_router
from config import settings
from middleware import setup_middleware

app = FastAPI(title="CloudEngine API", version="2.0.0")

setup_middleware(app)
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')

    with open(os.path.join(src_dir, "config.py"), "w", encoding="utf-8") as f:
        f.write('''"""应用配置"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "CloudEngine"
    DATABASE_URL: str = "mysql://root:password@localhost:3306/cloudengine"
    REDIS_URL: str = "redis://localhost:6379/0"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    SECRET_KEY: str = "your-secret-key"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
''')

    services_dir = os.path.join(src_dir, "services")
    os.makedirs(services_dir, exist_ok=True)

    with open(os.path.join(services_dir, "user_service.py"), "w", encoding="utf-8") as f:
        f.write('''"""用户服务"""
from typing import Optional
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user_data: UserCreate) -> User:
        user = User(**user_data.dict())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user = self.get_user(user_id)
        if user:
            for key, value in user_data.dict(exclude_unset=True).items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
''')

    with open(os.path.join(services_dir, "chat_service.py"), "w", encoding="utf-8") as f:
        f.write('''"""智能客服服务"""
from typing import List, Optional
from openai import OpenAI
from config import settings

class ChatService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.SECRET_KEY)
        self.model = "qwen3.6-plus"

    def chat(self, message: str, history: List[dict] = None) -> str:
        messages = history or []
        messages.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def chat_with_knowledge(self, message: str, knowledge: str,
                           history: List[dict] = None) -> str:
        system_prompt = f"""你是一个智能客服助手。请根据以下知识库内容回答用户问题。
如果知识库中没有相关信息，请诚实说明。

知识库内容：
{knowledge}"""
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content
''')

    models_dir = os.path.join(src_dir, "models")
    os.makedirs(models_dir, exist_ok=True)

    with open(os.path.join(models_dir, "user.py"), "w", encoding="utf-8") as f:
        f.write('''"""用户模型"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100))
    department = Column(String(50))
    position = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
''')

    print("✅ 代码仓库初始化完成")


def seed_all():
    print("🚀 开始初始化所有数据...\n")

    db = DatabaseEngine()
    seed_database(db)

    vector_db = VectorDBEngine()
    seed_vector_db(vector_db)

    keyword_engine = KeywordSearchEngine()
    seed_keyword_search(keyword_engine)

    seed_code_repo()

    print("\n🎉 所有数据初始化完成！")


if __name__ == "__main__":
    seed_all()
