import gradio as gr
from openai import OpenAI
import os
import datetime
import threading

# 应用实战：企业运营成本分析核算

# 提示：本案例运行消耗的Token较多,请选择合适的模型
# 浏览器中访问：http://127.0.0.1:7860，需要填入的数据可从三一重工.json和中联重科.json中获得

class CostAnalysisPipeline:
    def __init__(self, name):
        self.name = name

    # 调用大模型API
    @classmethod
    def get_completion(cls, messages):
        client = OpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"),
                        base_url="https://coding.dashscope.aliyuncs.com/v1")

        response = client.chat.completions.create(
            model='glm-5',
            messages=messages,
            temperature=0,  # 有数字计算，给较低的temperature
        )
        return response

    # 使用大模型进行问答
    @classmethod
    def LLM_QA(cls, llm_q):
        # 构建全局提示词模板
        qa_template = f"""
        ### 角色设定 ###
        你是一位拥有20年经验的资深注册会计师（CPA）及首席财务分析师。你精通上市公司财报审计、成本核算模型以及行业对标分析。
        
        ### 执行要求 ###
        - **数据准确性**：严格从给定的数据源提取数值，禁止编造。涉及计算时，需复核增长率和比率是否逻辑自洽。
        - **格式化**：优先使用 Markdown 表格展示对比数据，使用加粗字体突出核心结论。
        - **逻辑性**：分析需遵循“现象描述 -> 原因推导 -> 改进建议”的结构。
        - **专业性**：使用财务专业术语（如：CAGR、扣非、资产负债率等），分析需客观、严谨。
        - **保留追溯**：必须严格保留并标注财务数据的发表日期或报告期。
        
        ### 待处理问题 ###
        {llm_q}
        """
        try:
            # 打印开始询问大模型的时间
            messages = [{"role": "user", "content": qa_template}]
            # 调用OpenAI API获取回答
            response = cls.get_completion(messages)
            # 提取回答内容
            answer = response.choices[0].message.content.strip() if response.choices else "无法提供答案"
            # print(f"完整回答: {answer}")
            return answer
        except Exception as e:
            # 捕获并打印API调用异常
            print(f"{'*'*100}\nAPI调用失败: {e}\n{'*'*100}")
            return "无法提供答案"

    # 1.提取财务指标
    def extract_financial_data(self, report_text):
        print(f'{self.name}: 从财务报表中提取关键指标..')

        # 构建提取关键指标的提示词
        prompt = f'''
            ### 任务目标 ###
            你是一个精准的财务数据提取引擎。请从以下原始数据中提取关键财务指标，并以Markdown表格形式呈现。

            ### 摘要提取 ###
            提取SECURITY_NAME_ABBR作为企业名称、SECURITY_CODE作为股票代码。
            
            ### 财务指标提取清单 ###
            - 营业总收入 (TOTAL_OPERATE_INCOME)：保留单位为亿
            - 归母净利润 (PARENT_NETPROFIT)：保留单位为亿
            - 销售毛利率 (XSMLL)：保留单位为亿
            - 加权平均ROE (WEIGHTAVG_ROE)
            - 基本每股收益 (BASIC_EPS)
            - 扣非每股收益 (DEDUCT_BASIC_EPS)
            - 营业收入同比增长率 (YSTZ)
            - 净利润同比增长率 (SJLTZ)
                
            ### 要求 ###
            - 必须严格按照提取清单中指定的指标进行提取。
            
            ### 输出要求 ###
            1. 若包含多年/多季度数据，必须按时间顺序由近及远排列。
            2. 必须包含“发表日期/报告期”列以及所有提取指标列。
            3. 若数据缺失，请标注“未披露”。
            
            输入数据：{report_text}
        '''

        # 调用LLM_QA方法获取回答
        return self.LLM_QA(prompt)

    # 2.分析财务指标
    def analyze_financial_indicators(self, financial_data):
        print(f'{self.name}: 分析财务指标..')

        # 构建分析财务指标的提示词
        prompt = f'''
                    ### 任务目标 ###
                    作为资深财务分析师，请对提取的财务指标进行深度解读。

                    ### 分析维度 ###
                    1. **成长性分析**：对比营收和净利润的同比增长情况，判断增长是否由核心业务驱动。
                    2. **盈利稳定性**：通过EPS和净利润波动，分析企业是否存在非经常性损益依赖（对比扣非数据）。
                    3. **盈利质量**：分析毛利率走势，解读企业在产业链中的议价能力变化。

                    ### 格式要求 ###
                    - 使用“结论先行”的表达方式。
                    - 关键趋势请用表格汇总。

                    输入数据：{financial_data}
                '''
        # 调用 LLM_QA 方法获取回答
        return self.LLM_QA(prompt)

    # 3.预测未来趋势
    def predict_future_trends(self, financial_data):
        print(f'{self.name}: 预测未来趋势..')

        # 构建预测未来趋势的提示词
        prompt = f'''
            ### 任务目标 ###
            作为资深首席分析师，请基于现有的历史财务数据，对该企业未来三年（2026–2028）的业绩表现进行**审慎逻辑推演**。

            ### 第一步：历史基准复核 (Baseline) ###
            1. **计算 CAGR**：请先根据数据计算过去 3-5 年的营业收入和净利润的复合年均增长率（CAGR）。
            2. **周期定位**：识别当前处于工程机械周期的哪个阶段（复苏、波峰、衰退、筑底），并据此调整历史均值的权重。

            ### 第二步：多情景增长假设 (Scenario Analysis) ###
            请基于以下三个逻辑分支设定 2026-2028 的增长率，并在回复中明确说明你的假设条件：
            - **乐观情景**：国内基建投资回升 + 海外市场份额超预期扩张（建议参考历史高点增长率）。
            - **中性情景**：行业维持存量更新需求，出口平稳增长（建议参考历史 CAGR）。
            - **悲观情景**：房地产投资持续低迷 + 国际贸易壁垒增加（建议参考近两年最低增长率）。

            ### 第三步：数值预测输出 ###
            **要求：** 仅输出中性情景下的具体预测数值。
            | 预测年度 | 营业总收入 (亿元) | 营收同比增速 | 归母净利润 (亿元) | 净利润同比增速 | 关键驱动因素简述 |
            | :--- | :--- | :--- | :--- | :--- | :--- |
            | 2026E | | | | | |
            | 2027E | | | | | |
            | 2028E | | | | | |

            ### 执行约束 ###
            - **严禁凭空编造**：预测值必须与历史末期数据（2025Q3）具备逻辑连续性。
            - **单位统一**：金额一律以“人民币亿元”为单位。
            - **专业解释**：预测表下方需附带 200 字以内的“逻辑推导说明”，解释为何给出该增速。

            输入参考数据：{financial_data}
        '''
        
        # 调用LLM_QA方法获取回答
        return self.LLM_QA(prompt)

    # 4.优化成本
    def optimize_costs(self, financial_data):
        print(f'{self.name}: 成本分析与优化...')

        # 构建优化成本的提示词
        prompt = f'''
                    ### 任务目标 ###
                    进行成本结构分析，并提供针对性的降本增效建议。

                    ### 分析要点 ###
                    1. **成本效率评估**：结合毛利率和净利率，推算期间费用（销售、管理、研发、财务）的控制水平。
                    2. **业绩优化策略**：针对数据中暴露的弱点（如毛利下滑或费用过高），提出至少3条可落地的经营建议。

                    ### 输出要求 ###
                    - 建议需具备行业针对性（如机械制造业需关注供应链和原材料成本）。

                    输入数据：{financial_data}
                '''
        # 调用LLM_QA方法获取回答
        return self.LLM_QA(prompt)

    # 生成最终报告
    def generate_final_report(self, extracted_data, analysis_result, prediction_result, optimization_result):
        print(f'{self.name}: 生成最终报告..')

        # 构建生成最终报告的提示词
        prompt = f'''
                    ### 任务目标 ###
                    整合所有模块，生成一份专业、严谨的企业业绩分析报告。
                    
                    ### 输出要求 ###
                    - 必须包含报告结构中定义的部分。

                    ### 报告结构 ###
                    1. **报告名称**：使用提取的企业名称和股票代码来生成报告名称，格式为：企业名称（股票代码）企业业绩分析报告。
                    2. **核心摘要**：一句话总结企业当前财务健康状况。
                    3. **财务概况表**：汇总指标数据中的所有提取的财务历史数据。
                    4. **深度解读**：整合分析结果与趋势预测，包含4个维度：成长性、盈利质量、盈利稳定性和未来三年趋势预测。
                    5. **管理层建议**：整合成本优化方案。
                    
                    ### 排版要求 ###
                    - 使用二级标题分类。
                    - 必须保留数据的原始发表日期。
                    - 核心结论加粗显示。

                    输入材料：
                    - 指标数据：{extracted_data}
                    - 深度分析：{analysis_result}
                    - 趋势预测：{prediction_result}
                    - 优化建议：{optimization_result}
                '''
        # 调用LLM_QA方法获取回答
        return self.LLM_QA(prompt)

    # 分析数据
    def analyze_data(self, report_text, res):
        print(f'{"*"*80}\n{datetime.datetime.now()}')
        print(f'{self.name}: 开始分析数据..')

        # 1.提取财务指标
        financial_data = self.extract_financial_data(report_text)

        # 2.分析财务指标
        analysis_result = self.analyze_financial_indicators(financial_data)

        # 3.预测未来趋势
        prediction_result = self.predict_future_trends(financial_data)

        # 4.成本优化建议
        optimization_result = self.optimize_costs(financial_data)

        # 生成最终报告
        final_report = self.generate_final_report(
            financial_data, analysis_result, prediction_result, optimization_result
        )

        print("len(final_report): ", len(final_report))
        res.extend([final_report])


# 比较两个报告
def compare_reports(report1, report2):
    print(f'正在比较两个报告...')

    # 构建比较报告的提示词
    prompt = f'''
            ### 任务目标 ###
            对以下两家行业竞品（数据1 vs 数据2）进行对标分析（Benchmarking）。

            ### 对标维度 ###
            1. **规模地位**：营收与利润规模对比，确定谁是行业领跑者。
            2. **成长潜力**：对比近两年的CAGR，判断谁的扩张速度更快。
            3. **经营效率**：重点对比毛利率和ROE，分析谁的资产利用效率和盈利能力更强。
            4. **综合评级**：根据财务表现，给出各自的优势与劣势总结。

            ### 格式要求 ###
            - **必须使用对比表格展示核心指标**。
            - 结论需客观，注明数据引用的报表日期。

            数据1：{report1}
            数据2：{report2}
        '''
    # 调用LLM_QA方法获取回答
    return CostAnalysisPipeline.LLM_QA(prompt)

# 实际调用运行过程。比较两个报告
def compare(input1, input2):

    # 创建CostAnalysisPipeline实例
    pipeline1 = CostAnalysisPipeline('三一重工')
    pipeline2 = CostAnalysisPipeline('中联重科')

    # 使用多线程：让2个报告可以同时分析（节省时间）
    res1 = []  # 用来接收报告1的结果
    res2 = []  # 用来接收报告2的结果
    t1 = threading.Thread(target=pipeline1.analyze_data, args=(input1, res1))
    t2 = threading.Thread(target=pipeline2.analyze_data, args=(input2, res2))
    t1.start()  # 启动线程
    t2.start()
    t1.join()  # 等待让前面2个线程都结束
    t2.join()

    # 把多线程分析得到的报告用result1,result2,存储为final_report1,final_report2
    final_report1, = res1
    final_report2, = res2
    print(f"report1完成：{datetime.datetime.now()}\n-{'#'*80}")
    print(f"report2完成：{datetime.datetime.now()}\n-{'#'*80}")


    # 将报告1和报告2的结果写入md文件
    with open('result/final_report1.md', 'w', encoding='utf-8') as f:
        f.write(final_report1)
    with open('result/final_report2.md', 'w', encoding='utf-8') as f:
        f.write(final_report2)

    # 开始比较2个报告，并得到比较结果
    compare_result = compare_reports(final_report1, final_report2)
    print(f"compare报告比较完成：{datetime.datetime.now()}\n-{'#'*80}")

    # 将2个报告的比较结果，写入本地md文件
    with open('result/compare_result.md', 'w', encoding='utf-8') as f:
        f.write(compare_result)

    return compare_result


# 创建Gradio界面
def main():
    with gr.Blocks() as demo:
        gr.Markdown("## 企业业绩分析")
        with gr.Row():
            with gr.Column():
                # 输入框1，用于输入财务报表文本
                input1 = gr.Textbox(label="输入数据 1 (财务报表文本)", placeholder="请输入财务报表内容...")

            with gr.Column():
                # 输入框2，用于输入财务报表文本
                input2 = gr.Textbox(label="输入数据 2 (财务报表文本)", placeholder="请输入财务报表内容...")

        # 比较按钮
        compare_button = gr.Button("生成并比较报告")
        # 输出框，用于显示比较结果
        compare_output = gr.Markdown(label="比较结果")
        # 绑定比较按钮到compare函数
        compare_button.click(compare, inputs=[input1, input2], outputs=compare_output)

    demo.launch()
    # demo.launch(server_name="0.0.0.0", server_port=8080)


if __name__ == "__main__":
    main()

