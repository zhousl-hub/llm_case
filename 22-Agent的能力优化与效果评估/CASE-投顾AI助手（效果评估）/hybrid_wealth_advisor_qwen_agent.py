#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
混合智能体（Hybrid Agent）- 财富管理投顾AI助手

基于 qwen-agent 实现的混合型智能体，结合反应式架构的即时响应能力和深思熟虑架构的长期规划能力，
通过协调层动态切换处理模式，提供智能化财富管理咨询服务。

三层架构：
1. 底层（反应式）：即时响应客户查询，提供快速反馈
2. 中层（协调）：评估任务类型和优先级，动态选择处理模式
3. 顶层（深思熟虑）：进行复杂的投资分析和长期财务规划
"""

import os

# 规避本地代理（如 Clash）拦截 localhost，导致 Gradio startup-events 返回 502
for _proxy_key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'):
    os.environ.pop(_proxy_key, None)
os.environ['NO_PROXY'] = '127.0.0.1,localhost,::1'
os.environ['no_proxy'] = '127.0.0.1,localhost,::1'

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

import dashscope
from dashscope import Generation
from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
from qwen_agent.tools.base import BaseTool, register_tool

# 配置 DashScope
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
dashscope.api_key = DASHSCOPE_API_KEY
dashscope.timeout = 30

LLM_MODEL = "qwen-flash"
GUI_SERVER_NAME = "127.0.0.1"
GUI_SERVER_PORT = 7860

# 提示模板
ASSESSMENT_PROMPT = """你是一个财富管理投顾AI助手的协调层。请评估以下用户查询，确定其类型和应该采用的处理模式。

用户查询: {user_query}

请判断:
1. 查询类型:
   - "emergency": 紧急的或直接的查询，需要立即响应（如市场状况、账户信息、产品信息等）
   - "informational": 信息性的查询，需要特定领域知识（如税务政策、投资工具介绍等）
   - "analytical": 需要深度分析的查询（如投资组合优化、长期理财规划等）

2. 建议的处理模式:
   - "reactive": 适用于需要快速反应的查询
   - "deliberative": 适用于需要深度思考和分析的查询

请以JSON格式返回结果，包含以下字段:
- query_type: 查询类型（上述三种类型之一）
- processing_mode: 处理模式（上述两种模式之一）
- reasoning: 决策理由的简要说明
"""

DATA_COLLECTION_PROMPT = """你是一个财富管理投顾AI助手的数据收集模块。基于以下用户查询，确定需要收集哪些市场和财务数据进行深入分析。

用户查询: {user_query}

客户信息:
{customer_profile}

请确定需要收集的数据类型，例如:
- 资产类别表现数据
- 经济指标
- 行业趋势
- 历史回报率
- 风险指标
- 税收信息
- 其他相关数据

以JSON格式返回结果，包含以下字段:
- required_data_types: 需要收集的数据类型列表
- data_sources: 建议的数据来源列表
- collected_data: 模拟收集的数据（为简化示例，请生成合理的模拟数据）
"""

ANALYSIS_PROMPT = """你是一个财富管理投顾AI助手的分析引擎。请根据收集的数据对用户的投资情况进行深入分析。

用户查询: {user_query}

客户信息:
{customer_profile}

市场数据:
{market_data}

请提供全面的投资分析，包括:
1. 当前市场状况评估
2. 客户投资组合分析
3. 个性化投资建议
4. 风险评估
5. 预期结果和回报预测

以JSON格式返回分析结果，包含以下字段:
- market_assessment: 市场评估
- portfolio_analysis: 投资组合分析
- recommendations: 投资建议列表
- risk_analysis: 风险分析
- expected_outcomes: 预期结果
"""

RECOMMENDATION_PROMPT = """你是一个财富管理投顾AI助手。请根据深入分析结果，为客户准备最终的咨询建议。

用户查询: {user_query}

客户信息:
{customer_profile}

分析结果:
{analysis_results}

请提供专业、个性化且详细的投资建议，语言应友好易懂，避免过多专业术语。建议应包括:
1. 总体投资策略
2. 具体行动步骤
3. 资产配置建议
4. 风险管理策略
5. 时间框架
6. 预期收益
7. 后续跟进计划

返回格式应为自然语言文本，适合直接呈现给客户。
"""

# 示例客户画像数据
SAMPLE_CUSTOMER_PROFILES = {
    "customer1": {
        "customer_id": "C10012345",
        "risk_tolerance": "平衡型",
        "investment_horizon": "中期",
        "financial_goals": ["退休规划", "子女教育金"],
        "investment_preferences": ["ESG投资", "科技行业"],
        "portfolio_value": 1500000.0,
        "current_allocations": {
            "股票": 0.40,
            "债券": 0.30,
            "现金": 0.10,
            "另类投资": 0.20
        }
    },
    "customer2": {
        "customer_id": "C10067890",
        "risk_tolerance": "进取型",
        "investment_horizon": "长期",
        "financial_goals": ["财富增长", "资产配置多元化"],
        "investment_preferences": ["新兴市场", "高成长行业"],
        "portfolio_value": 3000000.0,
        "current_allocations": {
            "股票": 0.65,
            "债券": 0.15,
            "现金": 0.05,
            "另类投资": 0.15
        }
    }
}


# ====== 工具定义 ======

@register_tool('query_shanghai_index')
class QueryShanghaiIndexTool(BaseTool):
    """上证指数实时查询工具（模拟版），返回固定的行情数据"""

    description = '查询上证指数的最新行情数据，包括当前点位、涨跌和涨跌幅'
    parameters = []

    def call(self, params: str, **kwargs) -> str:
        name = "上证指数"
        price = "3125.62"
        change = "6.32"
        pct = "0.20"
        result = f"{name} 当前点位: {price}，涨跌: {change}，涨跌幅: {pct}%"
        print('工具调用结果:', result)
        return result


# ====== LLM 调用辅助 ======

def _extract_json_from_text(text: str) -> Dict[str, Any]:
    """从 LLM 输出中提取 JSON 对象"""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if code_block:
        return json.loads(code_block.group(1))

    brace_match = re.search(r'\{.*\}', text, re.DOTALL)
    if brace_match:
        return json.loads(brace_match.group(0))

    raise ValueError(f"无法从 LLM 输出中解析 JSON: {text[:200]}")


def _call_llm(prompt: str, json_output: bool = False) -> Any:
    """调用 DashScope 大模型"""
    response = Generation.call(
        model=LLM_MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        result_format='message',
    )
    if response.status_code != 200:
        raise RuntimeError(f"LLM 调用失败: {response.message}")

    content = response.output.choices[0].message.content
    if json_output:
        return _extract_json_from_text(content)
    return content


def _extract_assistant_text(response_messages: List[Dict[str, Any]]) -> str:
    """从 qwen-agent 响应消息中提取文本"""
    final_response = ""
    for msg in response_messages:
        if msg.get('role') != 'assistant':
            continue
        content = msg.get('content', '')
        if isinstance(content, str):
            final_response += content
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    if item.get('text'):
                        final_response += item['text']
                    elif item.get('content'):
                        final_response += item['content']
                elif isinstance(item, str):
                    final_response += item
    return final_response


# ====== 混合智能体核心流程 ======

def assess_query(user_query: str) -> Dict[str, Any]:
    """评估用户查询，确定类型和处理模式"""
    print("[DEBUG] 进入阶段: assess_query")
    prompt = ASSESSMENT_PROMPT.format(user_query=user_query)
    result = _call_llm(prompt, json_output=True)
    print("[DEBUG] LLM评估输出:", result)

    processing_mode = result.get("processing_mode", "reactive")
    if processing_mode not in ["reactive", "deliberative"]:
        processing_mode = "reactive"

    query_type = result.get("query_type", "emergency")
    if query_type not in ["emergency", "informational", "analytical"]:
        query_type = "emergency"

    print(f"[DEBUG] 分支判断: processing_mode={processing_mode}, query_type={query_type}")
    return {
        "query_type": query_type,
        "processing_mode": processing_mode,
        "reasoning": result.get("reasoning", ""),
    }


def get_reactive_system_prompt(customer_profile: Dict[str, Any]) -> str:
    """反应式处理模式的系统提示词"""
    customer_info = json.dumps(customer_profile, ensure_ascii=False, indent=2)
    return f"""你是一个财富管理投顾AI助手，专注于提供快速准确的响应。

## 客户信息
{customer_info}

## 工作要求
- 直接回答用户问题，语言简洁专业
- 当用户询问上证指数或大盘行情时，使用 query_shanghai_index 工具获取数据
- 结合客户画像给出个性化建议（如适用）
- 可提供相关的关键数据点和后续操作建议
"""


def init_reactive_agent(customer_profile: Dict[str, Any]) -> Assistant:
    """初始化反应式处理智能体（支持工具调用）"""
    llm_cfg = {
        'model': LLM_MODEL,
        'timeout': 30,
        'retry_count': 3,
    }
    return Assistant(
        llm=llm_cfg,
        name='财富管理投顾AI助手',
        description='快速响应型财富管理咨询服务',
        system_message=get_reactive_system_prompt(customer_profile),
        function_list=['query_shanghai_index'],
    )


def run_reactive_processing(user_query: str, customer_profile: Dict[str, Any]) -> str:
    """反应式处理模式，通过 qwen-agent 支持工具调用"""
    print("[DEBUG] 进入阶段: reactive_processing")
    agent = init_reactive_agent(customer_profile)
    messages = [{'role': 'user', 'content': user_query}]
    response_messages = []
    for response in agent.run(messages):
        response_messages = response
    return _extract_assistant_text(response_messages)


def run_deliberative_processing(user_query: str, customer_profile: Dict[str, Any]) -> str:
    """深思熟虑处理模式：数据收集 -> 深度分析 -> 生成建议"""
    print("[DEBUG] 进入阶段: deliberative_processing")
    customer_json = json.dumps(customer_profile, ensure_ascii=False, indent=2)

    # 数据收集
    print("[DEBUG] 进入阶段: collect_data")
    collect_prompt = DATA_COLLECTION_PROMPT.format(
        user_query=user_query,
        customer_profile=customer_json,
    )
    collect_result = _call_llm(collect_prompt, json_output=True)
    market_data = collect_result.get("collected_data", {})

    # 深度分析
    print("[DEBUG] 进入阶段: analyze_data")
    analysis_prompt = ANALYSIS_PROMPT.format(
        user_query=user_query,
        customer_profile=customer_json,
        market_data=json.dumps(market_data, ensure_ascii=False, indent=2),
    )
    analysis_results = _call_llm(analysis_prompt, json_output=True)

    # 生成建议
    print("[DEBUG] 进入阶段: generate_recommendations")
    recommend_prompt = RECOMMENDATION_PROMPT.format(
        user_query=user_query,
        customer_profile=customer_json,
        analysis_results=json.dumps(analysis_results, ensure_ascii=False, indent=2),
    )
    return _call_llm(recommend_prompt, json_output=False)


def run_wealth_advisor(user_query: str, customer_id: str = "customer1") -> Dict[str, Any]:
    """运行财富顾问混合智能体并返回结果"""
    customer_profile = SAMPLE_CUSTOMER_PROFILES.get(
        customer_id, SAMPLE_CUSTOMER_PROFILES["customer1"]
    )

    initial_state = {
        "user_query": user_query,
        "customer_profile": customer_profile,
        "query_type": None,
        "processing_mode": None,
        "market_data": None,
        "analysis_results": None,
        "final_response": None,
        "error": None,
    }

    try:
        assessment = assess_query(user_query)
        processing_mode = assessment["processing_mode"]
        query_type = assessment["query_type"]

        if processing_mode == "reactive":
            final_response = run_reactive_processing(user_query, customer_profile)
        else:
            final_response = run_deliberative_processing(user_query, customer_profile)

        return {
            **initial_state,
            "query_type": query_type,
            "processing_mode": processing_mode,
            "final_response": final_response,
        }
    except Exception as e:
        error_msg = str(e)
        print(f"捕获异常: {error_msg}")
        return {
            **initial_state,
            "error": f"执行过程中发生错误: {error_msg}",
            "final_response": "很抱歉，处理您的请求时出现了问题。",
        }


# ====== GUI 模式 ======

def init_wealth_advisor_agent(customer_profile: Dict[str, Any]) -> Assistant:
    """初始化财富顾问智能体（GUI 连续对话模式）"""
    customer_info = json.dumps(customer_profile, ensure_ascii=False, indent=2)
    system_prompt = f"""你是一个专业的财富管理投顾AI助手，具备混合智能处理能力。

## 客户信息
{customer_info}

## 你的能力

你具备两种处理模式，会根据查询类型自动选择：

### 1. 反应式处理模式（Reactive Mode）
适用于需要快速响应的查询，如市场状况、账户信息、产品说明等。
- 直接回答用户问题
- 如需市场数据，使用 query_shanghai_index 工具查询

### 2. 深思熟虑处理模式（Deliberative Mode）
适用于投资组合优化、长期理财规划、风险评估等复杂分析。
- 进行全面的市场评估和投资组合分析
- 提供个性化投资建议、风险管理策略和后续跟进计划

## 工具使用
- query_shanghai_index: 查询上证指数行情，当用户询问市场指数时使用

请根据用户查询智能选择处理模式，提供专业的财富管理咨询服务。"""

    llm_cfg = {
        'model': LLM_MODEL,
        'timeout': 30,
        'retry_count': 3,
    }
    agent = Assistant(
        llm=llm_cfg,
        name='财富管理投顾AI助手',
        description='混合智能体财富管理咨询服务',
        system_message=system_prompt,
        function_list=['query_shanghai_index'],
    )
    print("财富顾问智能体初始化成功！")
    return agent


def app_gui(customer_id: str = "customer1"):
    """图形界面模式，提供 Web 图形界面"""
    try:
        print("正在启动 Web 界面...")
        customer_profile = SAMPLE_CUSTOMER_PROFILES.get(
            customer_id, SAMPLE_CUSTOMER_PROFILES["customer1"]
        )
        agent = init_wealth_advisor_agent(customer_profile)

        chatbot_config = {
            'prompt.suggestions': [
                '今天上证指数的表现如何？',
                '我的投资组合中科技股占比是多少？',
                '请解释一下什么是ETF？',
                '根据当前市场情况，我应该如何调整投资组合以应对可能的经济衰退？',
                '考虑到我的退休目标，请评估我当前的投资策略并提供优化建议。',
                '我想为子女准备教育金，请帮我设计一个10年期的投资计划。',
            ]
        }

        print(f"客户类型: {customer_profile['risk_tolerance']} 投资者")
        print(f"Web 界面准备就绪，正在启动服务 ({GUI_SERVER_NAME}:{GUI_SERVER_PORT})...")
        WebUI(agent, chatbot_config=chatbot_config).run(
            server_name=GUI_SERVER_NAME,
            server_port=GUI_SERVER_PORT,
        )
    except Exception as e:
        print(f"启动 Web 界面失败: {str(e)}")
        print("若提示 502，请关闭系统代理后重试，或检查端口是否被占用")


# ====== TUI 模式 ======

def app_tui():
    """终端交互模式，使用显式混合路由处理每次查询"""
    try:
        print("=== 混合智能体 - 财富管理投顾AI助手 ===\n")
        print(f"使用模型：{LLM_MODEL}")
        print("框架：qwen-agent\n")
        print("-" * 50 + "\n")

        customer_id = "customer1"
        customer_choice = input("选择客户 (1: 平衡型投资者, 2: 进取型投资者，默认1): ").strip()
        if customer_choice == "2":
            customer_id = "customer2"

        customer_profile = SAMPLE_CUSTOMER_PROFILES[customer_id]
        print(f"\n客户类型: {customer_profile['risk_tolerance']} 投资者")
        print("已就绪，请输入您的问题（输入 'quit' 或 'exit' 退出）\n")

        while True:
            try:
                query = input('用户问题: ').strip()
                if query.lower() in ['quit', 'exit', '退出']:
                    print("再见！")
                    break
                if not query:
                    print('问题不能为空！')
                    continue

                print("正在处理您的请求...")
                start_time = datetime.now()
                result = run_wealth_advisor(query, customer_id)
                end_time = datetime.now()

                if result.get("error"):
                    print(f"处理过程中发生错误: {result['error']}")

                process_mode = result.get("processing_mode", "未知")
                if process_mode == "reactive":
                    print("【处理模式: 反应式】- 快速响应简单查询")
                elif process_mode == "deliberative":
                    print("【处理模式: 深思熟虑】- 深度分析复杂查询")

                print("\n=== 响应结果 ===\n")
                print(result.get("final_response", "未生成响应"))
                print(f"\n处理用时: {(end_time - start_time).total_seconds():.2f}秒\n")

            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"处理请求时出错: {str(e)}")
                print("请重试或输入新的问题\n")
    except Exception as e:
        print(f"启动终端模式失败: {str(e)}")


# ====== 主函数 ======

if __name__ == "__main__":
    app_gui()  # 图形界面模式（默认）
