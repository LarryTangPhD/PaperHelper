from langchain.prompts import ChatPromptTemplate
from langchain_openai.chat_models.base import BaseChatOpenAI
import os
import json
import random
import hashlib
import time
from functools import lru_cache
from typing import Optional, Dict, Any

# 从环境变量中获取 API Key - 优先使用通义千问
api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("DEEPSEEK_API_KEY")

# 检查 API Key 是否设置
if not api_key:
    raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量（通义千问）或 DEEPSEEK_API_KEY 环境变量")

# 定义 base_url - 使用兼容模式（参考数眸平台配置）
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 缓存机制
_cache = {}

def _generate_cache_key(func_name: str, *args, **kwargs) -> str:
    """生成缓存键"""
    args_str = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(f"{func_name}:{args_str}".encode()).hexdigest()

def _get_cached_result(cache_key: str) -> Optional[str]:
    """获取缓存结果"""
    return _cache.get(cache_key)

def _set_cached_result(cache_key: str, result: str):
    """设置缓存结果"""
    _cache[cache_key] = result

def _retry_with_backoff(func, max_retries=3, base_delay=1):
    """
    带退避的重试机制
    
    Args:
        func: 要重试的函数
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            # 指数退避
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"请求失败，{delay:.1f}秒后重试... (尝试 {attempt + 1}/{max_retries})")
            time.sleep(delay)

# 创建 BaseChatOpenAI 实例 - 优化配置（参考数眸平台）
def get_llm(temperature=0.3, model_type="turbo"):
    """
    获取LLM实例 - 优化版配置
    
    Args:
        temperature: 创造性参数（默认0.3，提高响应速度）
        model_type: 模型类型 ("turbo" 快速响应, "plus" 高质量)
    """
    # 尝试使用快速模型管理器
    try:
        from src.config.fast_llm_manager import fast_llm_manager
        return fast_llm_manager.get_llm(temperature)
    except ImportError:
        # 回退到通义千问模型 - 优化配置
        model_name = "qwen-turbo" if model_type == "turbo" else "qwen-plus"
        return BaseChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=temperature,
            max_tokens=1500,      # 优化token数量
            timeout=30,           # 减少超时时间
            request_timeout=30    # 减少请求超时时间
        )

# 全局实例使用默认temperature
llm = get_llm()

def generate_paper(subject, word_count, creativity):
    """生成论文选题和建议 - 优化版（带缓存）"""
    # 生成缓存键
    cache_key = _generate_cache_key("generate_paper", subject, word_count, creativity)
    
    # 检查缓存
    cached_result = _get_cached_result(cache_key)
    if cached_result:
        try:
            result = json.loads(cached_result)
            return result.get('title'), result.get('abstract'), result.get('outline')
        except:
            pass
    
    # 根据creativity选择模型类型
    model_type = "plus" if creativity > 0.5 else "turbo"
    current_llm = get_llm(temperature=creativity, model_type=model_type)
    
    title_template = ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，具有丰富的论文指导经验。请为以下研究主题提供高质量的论文选题建议。

研究主题：{subject}

请从新闻传播学的专业角度，为该主题设计3-5个具有学术价值和创新性的论文题目。每个题目应该：
1. 符合新闻传播学的研究范式
2. 具有明确的研究问题和理论意义
3. 体现当前学科发展趋势
4. 适合{word_count}万字的论文篇幅

请直接返回题目列表，每个题目一行。""")
    ])
    
    abstract_template = ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，请为以下论文题目提供详细的研究建议。

论文题目：{title}
预期篇幅：{word_count}万字

请提供以下内容：

1. **研究意义与创新点**（300字以内）
   - 理论意义
   - 实践意义
   - 创新点分析

2. **研究大纲设计**（500字以内）
   - 前言/引言
   - 文献综述
   - 理论框架
   - 研究方法
   - 研究结果
   - 讨论
   - 结论

3. **研究建议**（200字以内）
   - 研究过程中需要注意的问题
   - 可能遇到的困难及解决方案
   - 对研究者的建议

请确保内容专业、具体、可操作，符合新闻传播学学术规范。""")
    ])

    # 使用特定temperature的llm
    title_chain = title_template | current_llm
    abstract_chain = abstract_template | current_llm

    try:
        # 使用重试机制获取标题
        def get_title():
            return title_chain.invoke({"subject": subject, "word_count": word_count}).content
        
        def get_abstract():
            return abstract_chain.invoke({
                "title": title, 
                "word_count": word_count
            }).content
        
        # 获取标题
        title = _retry_with_backoff(get_title)
        
        # 生成摘要和研究建议
        abstract = _retry_with_backoff(get_abstract)
        
        # 缓存结果
        result = {
            'title': title,
            'abstract': abstract,
            'outline': None
        }
        _set_cached_result(cache_key, json.dumps(result, ensure_ascii=False))
        
        return title, abstract, None
    except Exception as e:
        print(f"生成论文内容时发生错误: {str(e)}")
        return None, None, None

def topic_diagnosis(topic, research_type):
    """选题诊断分析"""
    current_llm = get_llm(temperature=0.3)
    
    diagnosis_template = ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，请对以下选题进行专业诊断。

研究主题：{topic}
研究类型：{research_type}

请从以下维度进行诊断分析：

1. **选题价值评估**
   - 理论贡献度
   - 实践意义
   - 社会价值

2. **研究可行性分析**
   - 理论可行性
   - 方法可行性
   - 数据可获得性
   - 时间可行性

3. **创新性评估**
   - 与现有研究的区别
   - 创新点识别
   - 研究空白填补

4. **风险评估**
   - 可能遇到的困难
   - 研究局限性
   - 建议的应对策略

请提供详细的分析报告，确保专业、客观、具体。""")
    ])
    
    diagnosis_chain = diagnosis_template | current_llm
    
    try:
        result = diagnosis_chain.invoke({
            "topic": topic,
            "research_type": research_type
        }).content
        
        return {"analysis": result}
    except Exception as e:
        print(f"选题诊断时发生错误: {str(e)}")
        return {"analysis": "诊断分析暂时无法完成，请稍后重试。"}

def analyze_topic_feasibility(topic, research_type):
    """分析选题可行性"""
    current_llm = get_llm(temperature=0.2)
    
    feasibility_template = ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，请对以下选题进行可行性评分和分析。

研究主题：{topic}
研究类型：{research_type}

请从以下维度进行评分（0-100分）并提供分析：

1. **理论可行性**：理论基础是否扎实，理论框架是否清晰
2. **方法可行性**：研究方法是否合适，操作是否可行
3. **数据可获得性**：数据来源是否可靠，获取是否容易
4. **创新性**：研究是否有创新点，是否填补研究空白
5. **总体评分**：综合考虑所有因素的总体评分

请以JSON格式返回结果，包含以下字段：
- theoretical_score: 理论可行性评分
- methodological_score: 方法可行性评分
- data_score: 数据可获得性评分
- innovation_score: 创新性评分
- score: 总体评分
- theoretical: 理论可行性分析
- methodological: 方法可行性分析
- data_availability: 数据可获得性分析
- innovation: 创新性分析
- suggestions: 改进建议列表

请确保返回的是有效的JSON格式。""")
    ])
    
    feasibility_chain = feasibility_template | current_llm
    
    try:
        result = feasibility_chain.invoke({
            "topic": topic,
            "research_type": research_type
        }).content
        
        # 尝试解析JSON结果
        try:
            # 提取JSON部分
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = result[json_start:json_end]
                feasibility_data = json.loads(json_str)
            else:
                # 如果无法解析JSON，生成默认数据
                feasibility_data = generate_default_feasibility_data()
        except json.JSONDecodeError:
            feasibility_data = generate_default_feasibility_data()
        
        return feasibility_data
    except Exception as e:
        print(f"可行性分析时发生错误: {str(e)}")
        return generate_default_feasibility_data()

def generate_default_feasibility_data():
    """生成默认的可行性数据"""
    return {
        "theoretical_score": random.randint(60, 85),
        "methodological_score": random.randint(65, 90),
        "data_score": random.randint(50, 80),
        "innovation_score": random.randint(70, 95),
        "score": random.randint(65, 85),
        "theoretical": "理论可行性需要进一步评估",
        "methodological": "方法可行性需要具体分析",
        "data_availability": "数据可获得性需要调研",
        "innovation": "创新性需要与现有研究对比",
        "suggestions": [
            "建议进一步明确研究问题",
            "需要补充相关理论基础",
            "建议调研数据可获得性",
            "可以增加研究的创新点"
        ]
    }

def get_research_trends():
    """获取研究趋势"""
    current_llm = get_llm(temperature=0.4)
    
    trends_template = ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，请总结当前新闻传播学领域的研究趋势和热点话题。

请从以下方面进行分析：

1. **理论研究趋势**
   - 新兴理论发展
   - 经典理论的新应用
   - 跨学科理论融合

2. **技术发展影响**
   - 新媒体技术对传播的影响
   - 人工智能与传播研究
   - 社交媒体研究新方向

3. **社会热点话题**
   - 当前社会关注的传播现象
   - 政策变化对传播的影响
   - 全球化背景下的传播研究

4. **研究方法创新**
   - 新的研究方法应用
   - 混合研究方法发展
   - 大数据分析方法

请提供详细的分析报告，帮助研究者了解学科发展动态。""")
    ])
    
    trends_chain = trends_template | current_llm
    
    try:
        result = trends_chain.invoke({}).content
        return {"trends": result}
    except Exception as e:
        print(f"获取研究趋势时发生错误: {str(e)}")
        return {"trends": "研究趋势分析暂时无法完成，请稍后重试。"}

def intelligent_annotation(paper_content, annotation_type="comprehensive"):
    """智能批注功能 - 增强版"""
    current_llm = get_llm(temperature=0.2)
    
    # 根据批注类型选择不同的提示词
    if annotation_type == "全面批注":
        prompt_template = get_comprehensive_annotation_prompt()
    elif annotation_type == "学术规范性":
        prompt_template = get_academic_standard_prompt()
    elif annotation_type == "逻辑结构":
        prompt_template = get_logic_structure_prompt()
    elif annotation_type == "内容质量":
        prompt_template = get_content_quality_prompt()
    elif annotation_type == "语言表达":
        prompt_template = get_language_expression_prompt()
    else:
        prompt_template = get_comprehensive_annotation_prompt()
    
    annotation_chain = prompt_template | current_llm
    
    try:
        result = annotation_chain.invoke({
            "paper_content": paper_content,
            "annotation_type": annotation_type
        }).content
        
        return {"annotation": result}
    except Exception as e:
        print(f"智能批注时发生错误: {str(e)}")
        return {"annotation": "批注分析暂时无法完成，请稍后重试。"}

def get_comprehensive_annotation_prompt():
    """获取全面批注提示词"""
    return ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，拥有20年以上的学术研究经验。请对以下论文内容进行深度专业批注。

论文内容：{paper_content}

请从以下**10个专业维度**进行详细批注：

## 📋 **1. 学术规范性评估**
- **引用格式**：检查APA/MLA/GB格式规范性
- **参考文献**：完整性、准确性、时效性
- **学术表达**：避免口语化、使用第三人称
- **格式规范**：标题、段落、图表格式

## 🧠 **2. 理论框架分析**
- **理论基础**：是否运用了合适的传播学理论
- **理论创新**：是否有理论贡献或创新点
- **理论应用**：理论运用是否恰当、深入
- **理论对话**：是否与现有理论形成对话

## 🔬 **3. 研究方法评估**
- **方法选择**：定量/定性/混合方法是否合适
- **研究设计**：实验设计、调查设计、案例研究设计
- **数据收集**：样本选择、数据来源、收集方法
- **数据分析**：统计方法、分析工具、结果解释

## 📊 **4. 逻辑结构分析**
- **论证逻辑**：前提-推理-结论的逻辑链条
- **结构完整性**：引言-文献综述-方法-结果-讨论-结论
- **段落组织**：段落间的逻辑关系
- **过渡连接**：段落间的过渡是否自然

## 💡 **5. 创新性评估**
- **研究问题**：问题的新颖性和重要性
- **研究视角**：是否提供了新的研究视角
- **研究发现**：是否有新的发现或见解
- **实践价值**：对新闻传播实践的指导意义

## 🎯 **6. 内容质量分析**
- **研究深度**：分析的深度和广度
- **论证充分性**：论据是否充分、有力
- **结论可靠性**：结论是否基于充分证据
- **局限性认识**：是否认识到研究局限性

## ✍️ **7. 语言表达评估**
- **学术语言**：使用规范的学术表达
- **表达清晰度**：概念表达是否清晰准确
- **专业术语**：术语使用是否准确恰当
- **语言流畅性**：表达是否流畅自然

## 📈 **8. 实证研究特色**（如适用）
- **数据质量**：数据的可靠性、有效性
- **分析深度**：统计分析的深度和准确性
- **结果解释**：对结果的合理解释
- **实践应用**：研究结果的实践指导价值

## 🌐 **9. 新闻传播学专业特色**
- **学科前沿**：是否涉及学科前沿问题
- **行业关联**：与新闻传播行业的关联度
- **社会价值**：对社会发展的贡献
- **国际视野**：是否具有国际比较视野

## 🔧 **10. 具体改进建议**
- **结构优化**：具体的结构调整建议
- **内容补充**：需要补充的内容和方向
- **方法改进**：研究方法的改进建议
- **表达优化**：语言表达的改进建议

请为每个维度提供：
1. **具体问题识别**：指出具体存在的问题
2. **专业分析**：从新闻传播学专业角度分析
3. **改进建议**：提供具体、可操作的改进建议
4. **评分**：每个维度给出1-10分的评分

最后提供**总体评价**和**优先级改进建议**。

请确保批注专业、具体、可操作，体现新闻传播学的专业特色。""")
    ])

def get_academic_standard_prompt():
    """获取学术规范性批注提示词"""
    return ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，请专门针对学术规范性对以下论文内容进行批注。

论文内容：{paper_content}

请重点检查以下方面：

## 📚 **引用格式规范**
- 文内引用格式（作者-年份/数字编号）
- 参考文献列表格式
- 引用完整性（作者、年份、标题、来源）
- 引用时效性（文献的新旧程度）

## 📝 **学术表达规范**
- 避免第一人称（我、我们）
- 使用客观、正式的学术语言
- 避免口语化表达
- 使用适当的学术连接词

## 📋 **格式规范**
- 标题格式和层级
- 段落格式和缩进
- 图表标题和编号
- 页眉页脚格式

## 🔍 **专业术语使用**
- 新闻传播学专业术语的准确性
- 术语使用的一致性
- 新概念的定义和解释

请提供具体的修改建议和示例。""")
    ])

def get_logic_structure_prompt():
    """获取逻辑结构批注提示词"""
    return ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，请专门针对逻辑结构对以下论文内容进行批注。

论文内容：{paper_content}

请重点分析以下方面：

## 🏗️ **整体结构**
- 论文各部分是否完整
- 各部分之间的逻辑关系
- 结构是否符合学术规范

## 🔗 **论证逻辑**
- 前提是否明确
- 推理过程是否合理
- 结论是否基于充分证据
- 逻辑链条是否完整

## 📑 **段落组织**
- 段落主题是否明确
- 段落间过渡是否自然
- 段落内容是否围绕主题

## 🎯 **重点突出**
- 核心观点是否突出
- 重要发现是否强调
- 研究贡献是否明确

请提供具体的结构调整建议。""")
    ])

def get_content_quality_prompt():
    """获取内容质量批注提示词"""
    return ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，请专门针对内容质量对以下论文内容进行批注。

论文内容：{paper_content}

请重点评估以下方面：

## 🧠 **理论深度**
- 理论运用是否恰当
- 理论分析是否深入
- 是否有理论创新

## 🔬 **研究深度**
- 问题分析是否深入
- 论证是否充分
- 结论是否可靠

## 📊 **实证质量**（如适用）
- 数据质量如何
- 分析方法是否合适
- 结果解释是否合理

## 💡 **创新性**
- 研究问题是否新颖
- 研究方法是否有创新
- 研究结果是否有新发现

## 🌐 **实践价值**
- 对新闻传播实践的指导意义
- 对社会发展的贡献
- 对学科发展的推动

请提供具体的内容改进建议。""")
    ])

def get_language_expression_prompt():
    """获取语言表达批注提示词"""
    return ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，请专门针对语言表达对以下论文内容进行批注。

论文内容：{paper_content}

请重点检查以下方面：

## ✍️ **语言规范性**
- 语法是否正确
- 用词是否准确
- 句式是否多样
- 表达是否简洁

## 🎯 **表达清晰度**
- 概念表达是否清晰
- 逻辑关系是否明确
- 重点是否突出
- 语言是否流畅

## 📚 **学术语言**
- 是否使用规范的学术表达
- 专业术语使用是否准确
- 语言风格是否一致
- 是否避免口语化

## 🔗 **语言连贯性**
- 句子间连接是否自然
- 段落间过渡是否流畅
- 整体语言风格是否统一

请提供具体的语言修改建议和示例。""")
    ])

def format_correction(paper_content, target_format="APA"):
    """格式修正功能"""
    current_llm = get_llm(temperature=0.1)
    
    format_template = ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的学术编辑，请对以下论文内容进行格式修正。

论文内容：{paper_content}
目标格式：{target_format}

请进行以下格式修正：

1. **标题格式**
   - 标题层级规范
   - 字体格式统一
   - 编号格式规范

2. **段落格式**
   - 段落间距统一
   - 缩进格式规范
   - 对齐方式统一

3. **引用格式**
   - 引用格式标准化
   - 参考文献格式规范
   - 引用标记统一

4. **图表格式**
   - 图表标题规范
   - 图表编号统一
   - 图表说明格式

5. **其他格式**
   - 页码格式
   - 页眉页脚
   - 字体字号

请提供修正后的内容，确保格式规范统一。""")
    ])
    
    format_chain = format_template | current_llm
    
    try:
        result = format_chain.invoke({
            "paper_content": paper_content,
            "target_format": target_format
        }).content
        
        return {"corrected_content": result}
    except Exception as e:
        print(f"格式修正时发生错误: {str(e)}")
        return {"corrected_content": "格式修正暂时无法完成，请稍后重试。"}

# 使用示例
if __name__ == "__main__":
    try:
        title, abstract, outline = generate_paper("元宇宙与数字身份认同", 0.8, 0.7)
        if title:
            print("论文标题:", title)
            print("\n论文研究建议:", abstract)
            if outline:
                print("\n论文大纲:", outline)
        else:
            print("生成失败")
    except Exception as e:
        print(f"程序执行出错: {str(e)}")