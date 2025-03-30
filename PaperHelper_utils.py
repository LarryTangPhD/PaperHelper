from langchain.prompts import ChatPromptTemplate
from langchain_openai.chat_models.base import BaseChatOpenAI
import os

# 从环境变量中获取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

# 检查 DEEPSEEK_API_KEY 是否设置
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")

# 定义 base_url
base_url = "https://api.deepseek.com"

# 创建 BaseChatOpenAI 实例 - 不直接设置temperature，让它在函数中创建
def get_llm(temperature=0.7):
    return BaseChatOpenAI(
        model="deepseek-chat",
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=temperature
    )

# 全局实例使用默认temperature
llm = get_llm()

def generate_paper(subject, word_count, creativity):
    # 为这次调用创建特定temperature的llm实例
    current_llm = get_llm(temperature=creativity)
    
    title_template = ChatPromptTemplate.from_messages(
        [
            ("human", "请从标准、规范的研究型论文的一般撰写范式出发，为下面这个论文创意方向提供一些高质量的论文写作建议，注意应当符合新闻传播学研究论文的标准范式。下面是该主题的相关信息 ：###'{subject}'###")
        ]
    )
    abstract_template = ChatPromptTemplate.from_messages(
        [
            ("human",
             """角色定位：你是一位专业的学术研究助手，具备深厚的专业知识和丰富的研究经验。你的任务是为一篇新闻传播学领域的学术论文提供撰写建议，包括题目设计与论文框架建议。
任务描述：
根据以下大致给定的论文方向，为这篇草拟中的学术论文提供一份详细的研究撰写建议。论文大致方向为：{title}，全文期望字数为 {word_count}万字


1. 研究论文拟定题目推荐（列在回答的第一部分，不超过100字）

为{title}这个大致方向设计3-5个符合新闻传播学特征的高水平论文题目

2. 研究意义与创新点（列在回答的第二部分，不超过300字）

跟据学术领域现有成果以及当前社会发展现状，分别为刚刚生成的题目撰写清楚研究意义

3. 研究大纲设计（列在回答的第三部分，不超过500字）

请围绕此前生成的题目推荐，为其中具有最强研究意义的题目撰写一份论文大纲，包括但不限于：
1. 前言/引言
2. 文献综述
3. 理论框架
4. 研究方法
5. 研究结果
6. 讨论
7. 结论

对于每个部分，请提供2-3个子标题和简短说明，确保大纲的逻辑性和完整性。大纲应体现新闻传播学领域的学术规范和研究思路，并与论文主题紧密相关。请特别关注理论框架的构建和研究方法的选择，确保它们适合该研究主题。

大纲应当条理清晰，层次分明，每个部分都有明确的研究内容和目标。最终大纲应为研究者提供一个全面而具体的研究路线图。

注意：你每次的生成内容篇幅不要超过1000字，尤其是要参考对方预想中的总字数来进行设计。提供内容紧密围绕新闻传播学领域（人文社科）的学术规范来指定，需要特别强调论文的理论意义和研究方案设计的合理性。

""")
        ]
    )

    # 使用特定temperature的llm
    title_chain = title_template | current_llm
    abstract_chain = abstract_template | current_llm

    try:
        # 获取标题
        title = title_chain.invoke({"subject": subject}).content

        # 生成摘要和研究建议
        abstract = abstract_chain.invoke({
            "title": title, 
            "word_count": word_count
        }).content
        
        # 返回结果，不包含outline
        return title, abstract, None
    except Exception as e:
        print(f"生成论文内容时发生错误: {str(e)}")
        # 可以添加更多详细的错误信息，比如API状态等
        return None, None, None

# 使用示例
#try:
    title, abstract, outline = generate_paper("元宇宙与数字身份认同", 5000, 0.7)
    if title:
        print("论文标题:", title)
        print("\n论文研究建议:", abstract)
        if outline:  # 添加条件检查，因为outline现在可能是None
            print("\n论文大纲:", outline)
    else:
        print("生成失败")
#except Exception as e:
    print(f"程序执行出错: {str(e)}")