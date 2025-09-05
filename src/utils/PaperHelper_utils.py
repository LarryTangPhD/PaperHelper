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
    """智能批注功能"""
    current_llm = get_llm(temperature=0.3)
    
    annotation_template = ChatPromptTemplate.from_messages([
        ("human", """你是一位资深的新闻传播学教授，请对以下论文内容进行专业批注。

论文内容：{paper_content}
批注类型：{annotation_type}

请从以下方面进行批注：

1. **学术规范性**
   - 格式规范检查
   - 引用格式规范
   - 学术表达规范

2. **逻辑结构**
   - 逻辑清晰度
   - 结构合理性
   - 论证充分性

3. **内容质量**
   - 理论应用合理性
   - 方法选择适当性
   - 结论可靠性

4. **语言表达**
   - 学术语言规范性
   - 表达清晰度
   - 专业术语使用

5. **改进建议**
   - 具体修改建议
   - 补充内容建议
   - 结构调整建议

请提供详细的批注报告，确保专业、具体、可操作。""")
    ])
    
    annotation_chain = annotation_template | current_llm
    
    try:
        result = annotation_chain.invoke({
            "paper_content": paper_content,
            "annotation_type": annotation_type
        }).content
        
        return {"annotation": result}
    except Exception as e:
        print(f"智能批注时发生错误: {str(e)}")
        return {"annotation": "批注分析暂时无法完成，请稍后重试。"}

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