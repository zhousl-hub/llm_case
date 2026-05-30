import streamlit as st
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import AgenticSearchAgent
from core.logger import Logger

st.set_page_config(
    page_title="Agentic Search - 智能企业搜索",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-badge {
        display: inline-block;
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 0.5rem;
    }
    .trace-label {
        display: inline-block;
        padding: 0.1rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.3rem;
    }
    .trace-llm { background: #E8F5E9; color: #2E7D32; }
    .trace-tool { background: #FFF3E0; color: #E65100; }
    .trace-result { background: #E3F2FD; color: #1565C0; }
    .trace-warn { background: #FFEBEE; color: #C62828; }
    .trace-prompt { background: #F3E5F5; color: #6A1B9A; }
    .trace-final { background: #E8F5E9; color: #1B5E20; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)


def get_agent():
    return AgenticSearchAgent()


def get_logger():
    return Logger()


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "is_searching" not in st.session_state:
        st.session_state.is_searching = False


def perform_search(agent, question):
    status_area = st.empty()
    prompt_area = st.empty()
    rounds_area = st.empty()
    final_area = st.empty()

    all_tool_calls = []
    round_idx = 0

    try:
        for step in agent.search_stream(question):
            if step["step"] == "init":
                status_area.info("🔄 Agent 推理决策进行中...")

                prompt_text = step.get("system_prompt", "")
                with prompt_area.container():
                    st.markdown("##### 📤 用户问题")
                    st.info(step.get("question", question))
                    st.markdown("##### <span class='trace-label trace-prompt'>⚙️ 1. System Prompt 生成</span>", unsafe_allow_html=True)
                    st.caption(f"当前时间: {step.get('timestamp', 'N/A')}  |  共 {len(prompt_text)} 字符")
                    with st.expander("📋 查看完整 System Prompt", expanded=False):
                        st.code(prompt_text, language="markdown")

            elif step["step"] == "tool_call":
                all_tool_calls.append(step)
                round_idx = step["round"]

                with rounds_area.container():
                    for i, tc in enumerate(all_tool_calls):
                        is_same_round = (i == 0) or (all_tool_calls[i - 1]["round"] != tc["round"])
                        if is_same_round:
                            st.markdown(f"---")
                            st.markdown(f"##### <span class='trace-label trace-llm'>🧠 2.{tc['round']} 第 {tc['round']} 轮 — Qwen 模型推理</span>", unsafe_allow_html=True)
                            llm_text = tc.get("llm_text_content", "")
                            if llm_text:
                                st.caption(f"LLM 推理: {llm_text[:120]}")
                            with st.expander("📡 Qwen API 原始响应 JSON"):
                                st.code(tc.get("llm_raw_response", ""), language="json")

                        st.markdown(f"<span class='trace-label trace-tool'>🔧 执行工具: **{tc['tool_name']}**</span>", unsafe_allow_html=True)
                        st.markdown("**调用参数:**")
                        st.json(tc.get("arguments", {}))
                        st.markdown("**执行结果:**")
                        result_raw = tc.get("result", "")
                        try:
                            result_json = json.loads(result_raw)
                            if isinstance(result_json, dict) and "summary" in result_json:
                                s = result_json["summary"]
                                c1, c2, c3 = st.columns(3)
                                c1.metric("总收入", f"{s.get('total_income', 0):,} 元")
                                c2.metric("总支出", f"{s.get('total_expense', 0):,} 元")
                                c3.metric("记录数", s.get("count", 0))
                            else:
                                with st.expander("📊 查看完整结果 JSON"):
                                    st.code(result_raw, language="json")
                        except (json.JSONDecodeError, TypeError):
                            st.text(result_raw[:500])

            elif step["step"] == "fallback":
                with rounds_area.container():
                    st.markdown(f"<span class='trace-label trace-warn'>⚠️ API 不可用，降级到本地 {step.get('intent', '')} 搜索</span>", unsafe_allow_html=True)

            elif step["step"] == "final":
                status_area.success(f"✅ 搜索完成（共 {step.get('round', 0)} 轮）")
                with final_area.container():
                    st.markdown("---")
                    st.markdown("### <span class='trace-label trace-final'>🎯 3. 最终回答生成</span>", unsafe_allow_html=True)

                    prompt_type = step.get("final_prompt_type", "模型生成最终回答")
                    st.info(f"**生成方式**: {prompt_type}")

                    if step.get("force_prompt"):
                        st.markdown("**🔔 系统追加的强制提示词:**")
                        st.code(step["force_prompt"], language="text")

                    st.markdown("##### 📡 Qwen API 最终响应（生成最终回答的完整 API 返回）")
                    with st.expander("查看 Qwen API 原始响应 JSON（最终回答生成时刻）", expanded=False):
                        st.code(step.get("llm_raw_response", ""), language="json")

                    st.markdown("##### 📋 生成最终回答时的完整对话上下文（发送给 LLM 的 messages 数组）")
                    with st.expander("查看完整对话消息上下文", expanded=True):
                        messages_ctx = step.get("final_messages_context", [])
                        for m in messages_ctx:
                            idx = m.get("index", "?")
                            role = m.get("role", "?")
                            role_emoji = {"system": "⚙️", "user": "👤", "assistant": "🤖", "tool": "🔧"}.get(role, "❓")
                            full_content = m.get("content", "")

                            if role == "assistant" and m.get("tool_calls"):
                                st.markdown(f"**{role_emoji} [{idx}] {role} — 工具调用决策**")
                                st.code(full_content, language="json")
                                for tc in m["tool_calls"]:
                                    st.caption(f"     🔨 调用工具: **{tc['tool_name']}** | 参数: {json.dumps(tc['arguments'], ensure_ascii=False)}")
                            elif role == "tool":
                                st.markdown(f"**{role_emoji} [{idx}] {role} — 工具返回数据**")
                                try:
                                    parsed = json.loads(full_content)
                                    st.json(parsed)
                                except (json.JSONDecodeError, TypeError):
                                    st.code(full_content, language="json")
                            else:
                                st.markdown(f"**{role_emoji} [{idx}] {role}**")
                                st.code(full_content, language="text")

                    st.markdown("---")
                    st.markdown("### 📝 最终回答")
                    st.markdown(step.get("final_answer", ""))
                return step.get("final_answer", "")

    except Exception as e:
        status_area.error(f"搜索异常: {e}")
        return f"搜索过程中出现错误：{str(e)}"

    # 达到最大轮数
    status_area.warning(f"⚠️ 达到最大搜索轮数")
    return "搜索已达到最大轮数，请尝试更精确的问题。"


init_session_state()
agent = get_agent()
logger = get_logger()

st.markdown('<p class="main-header">🔍 Agentic Search</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">基于 Qwen 模型推理决策的智能企业搜索系统 — 完整过程可视化</p>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    question = st.text_input(
        "请输入您的问题：",
        placeholder="例如：本周的支付数据情况如何？",
        label_visibility="collapsed",
        key="question_input"
    )

with col2:
    search_button = st.button("🔍 搜索", type="primary", use_container_width=True)

if search_button and question:
    st.session_state.is_searching = True

    final_answer = perform_search(agent, question)

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": final_answer})
    st.session_state.is_searching = False

st.divider()

st.markdown("### 💬 对话历史")

if st.session_state.messages:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])
else:
    st.info("👆 请在上方输入问题开始搜索")

with st.sidebar:
    st.markdown("### 📚 数据源")
    st.markdown("""
    <span class="source-badge">📊 SQLite数据库</span>
    <span class="source-badge">🔮 向量数据库</span>
    <span class="source-badge">🔎 关键词索引</span>
    <span class="source-badge">💼 企业系统</span>
    <span class="source-badge">📝 代码仓库</span>
    """, unsafe_allow_html=True)

    st.markdown("### ℹ️ 系统信息")
    st.markdown("""
    - **模型**: Qwen 3.6 Plus
    - **最大搜索轮次**: 20
    - **降级模式**: 本地搜索（当API不可用时）
    - **过程追踪**: 完整显示所有推理步骤
    """)

    st.markdown("### 📊 搜索历史")

    if st.session_state.messages:
        for i, msg in enumerate(reversed(st.session_state.messages[-10:])):
            avatar = "👤" if msg["role"] == "user" else "🤖"
            content_preview = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
            st.markdown(f"**{avatar}** {content_preview}")
            st.markdown("---")
    else:
        st.write("暂无搜索历史")

    if st.button("🗑️ 清除历史", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### 🔧 状态")
    if st.session_state.is_searching:
        st.markdown('<p class="status-running">🔄 搜索中...</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-complete">✅ 就绪</p>', unsafe_allow_html=True)
