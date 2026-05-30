from __future__ import annotations
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seed_data_large import seed_all_large
from core.agent import AgenticSearchAgent


def main():
    print("=" * 60)
    print("  Agentic Search - 智能企业搜索助手")
    print("  基于Qwen模型的推理决策式多源搜索系统")
    print("=" * 60)

    if not os.environ.get("DASHSCOPE_API_KEY"):
        print("\n[!] 请设置环境变量 DASHSCOPE_API_KEY")
        print("    export DASHSCOPE_API_KEY=your_api_key")
        print("    可选: export DASHSCOPE_BASE_URL=your_base_url")
        print("          export DASHSCOPE_MODEL=your_model")
        print()

    print("\n[*] 正在初始化数据...")
    seed_all_large()

    agent = AgenticSearchAgent()

    print("\n" + "=" * 60)
    print("  系统就绪！输入问题开始搜索，输入 'quit' 退出")
    print("  可搜索的数据源:")
    print("    1. SQLite数据库 (员工/部门/项目/合同/产品)")
    print("    2. 向量数据库 (公司信息/技术文档/会议纪要)")
    print("    3. 关键词索引 (公司政策/技术文章)")
    print("    4. 代码仓库 (源代码文件)")
    print("    5. 企业系统 (HR/财务/项目/Wiki)")
    print("    6. 操作日志")
    print("=" * 60)

    while True:
        try:
            question = input("\n[?] 请输入您的问题: ").strip()
            if not question:
                continue
            if question.lower() in ["quit", "exit", "q"]:
                print("[*] 再见！")
                break

            answer = agent.search(question, verbose=True)
        except KeyboardInterrupt:
            print("\n[*] 再见！")
            break
        except Exception as e:
            print(f"\n[!] 错误: {e}")


if __name__ == "__main__":
    main()
