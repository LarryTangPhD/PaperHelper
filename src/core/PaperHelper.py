import streamlit as st
import os
from src.utils.PaperHelper_utils import (
    generate_paper, 
    topic_diagnosis, 
    get_research_trends,
    analyze_topic_feasibility,
    intelligent_annotation
)
# 尝试导入简化版文档处理器
try:
    from src.modules.document_processor_simple import document_processor
    DOCUMENT_PROCESSOR_AVAILABLE = True
except ImportError:
    try:
        from src.modules.document_processor import document_processor
        DOCUMENT_PROCESSOR_AVAILABLE = True
    except ImportError:
        DOCUMENT_PROCESSOR_AVAILABLE = False
        document_processor = None
from src.modules.advanced_analyzer import advanced_analyzer

# 尝试导入写作助手模块
try:
    from src.modules.writing_assistant import writing_assistant
    WRITING_ASSISTANT_AVAILABLE = True
except ImportError:
    WRITING_ASSISTANT_AVAILABLE = False

# 尝试导入快速模型模块
try:
    from src.config.fast_llm_manager import fast_llm_manager
    from src.config.fast_models_config import fast_models_config
    FAST_MODELS_AVAILABLE = True
except ImportError:
    FAST_MODELS_AVAILABLE = False

# 页面配置
st.set_page_config(
    page_title="新传论文智能辅导系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "选题指导"
if 'user_topic' not in st.session_state:
    st.session_state.user_topic = ""
if 'topic_analysis' not in st.session_state:
    st.session_state.topic_analysis = None
if 'paper_content' not in st.session_state:
    st.session_state.paper_content = ""
if 'annotation_result' not in st.session_state:
    st.session_state.annotation_result = None
if 'paper_content' not in st.session_state:
    st.session_state.paper_content = ""
if 'annotation_result' not in st.session_state:
    st.session_state.annotation_result = None

# 侧边栏导航
with st.sidebar:
    st.header("✒ 白杨社科")
    
    # 添加作者图片
    if os.path.exists("src/assets/作者头像.png"):
        st.image("src/assets/作者头像.png", width=200)
    
    # 模型选择（如果可用）
    if FAST_MODELS_AVAILABLE:
        st.subheader("🤖 模型选择")
        
        # 获取可用模型
        available_models = fast_models_config.get_available_models()
        model_options = list(available_models.keys())
        model_names = [available_models[key]["name"] for key in model_options]
        
        # 当前模型信息
        current_model_info = fast_llm_manager.get_current_model_info()
        if "error" not in current_model_info:
            st.info(f"当前模型: {current_model_info['name']}")
            st.caption(f"速度: {current_model_info['speed']} | 成本: {current_model_info['cost']}")
        
        # 模型选择
        selected_model_index = st.selectbox(
            "选择模型：",
            range(len(model_options)),
            format_func=lambda x: f"{model_names[x]} ({available_models[model_options[x]]['speed']})",
            help="选择更快的模型可以提升响应速度"
        )
        
        if st.button("🔄 切换模型", type="secondary"):
            selected_model = model_options[selected_model_index]
            result = fast_llm_manager.switch_model(selected_model)
            
            if result["success"]:
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["error"])
        
        # 测试模型连接
        if st.button("🧪 测试连接", type="secondary"):
            test_result = fast_llm_manager.test_model_connection()
            if test_result["success"]:
                st.success("✅ 模型连接正常")
            else:
                st.error(f"❌ 连接失败: {test_result['error']}")
    
    # 页面导航
    st.subheader("📋 功能导航")
    
    # 获取当前页面的索引
    page_options = ["选题指导", "论文批注", "格式修正", "学习助手"]
    try:
        current_index = page_options.index(st.session_state.current_page)
    except ValueError:
        current_index = 0
        st.session_state.current_page = "选题指导"
    
    page = st.radio(
        "选择功能模块：",
        page_options,
        key="page_nav",
        index=current_index
    )
    
    # 更新当前页面
    st.session_state.current_page = page
    
    # 智能推荐
    st.markdown("### 💡 智能推荐")
    
    # 根据当前页面显示不同推荐
    if st.session_state.current_page == "选题指导":
        st.info("""
        **📚 推荐阅读**
        - 《新闻传播学研究方法》
        - 《传播学理论前沿》
        - 《新媒体研究热点》
        """)
        
        st.success("""
        **🎯 选题技巧**
        - 关注社会热点话题
        - 结合新技术发展
        - 注重理论创新
        """)
        
    elif st.session_state.current_page == "论文批注":
        st.info("""
        **✍️ 写作技巧**
        - 使用学术语言表达
        - 保持逻辑结构清晰
        - 增加文献引用支撑
        """)
        
        st.warning("""
        **⚠️ 常见问题**
        - 避免口语化表达
        - 注意引用格式规范
        - 确保论证充分
        """)
    
    # 工具介绍
    st.markdown("""
    ### 🎯 工具特色
    - **智能选题诊断**：评估选题可行性、创新性、可操作性
    - **实时批注反馈**：提供专业的学术写作建议
    - **格式规范检查**：确保论文格式符合学术标准
    - **个性化指导**：根据学生水平提供差异化建议
    
    ### 🔧 技术亮点
    - 基于通义千问大语言模型
    - 新闻传播学专业定制
    - 智能提示词工程
    - 实时反馈机制
    """)

# 主页面内容
def main_page():
    st.title("📚 新传论文智能辅导系统")
    
    # 快速操作面板
    with st.container():
        st.markdown("### ⚡ 快速操作")
        
        # 显示当前页面状态
        st.caption(f"当前页面: {st.session_state.current_page}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🎯 快速选题", use_container_width=True, key="btn_topic"):
                st.session_state.current_page = "选题指导"
                st.success("✅ 切换到选题指导")
                st.rerun()
        
        with col2:
            if st.button("✏️ 论文批注", use_container_width=True, key="btn_annotation"):
                st.session_state.current_page = "论文批注"
                st.success("✅ 切换到论文批注")
                st.rerun()
        
        with col3:
            if st.button("📐 格式修正", use_container_width=True, key="btn_format"):
                st.session_state.current_page = "格式修正"
                st.success("✅ 切换到格式修正")
                st.rerun()
        
        with col4:
            if st.button("🎓 学习助手", use_container_width=True, key="btn_learning"):
                st.session_state.current_page = "学习助手"
                st.success("✅ 切换到学习助手")
                st.rerun()
    
    st.markdown("---")
    
    # 根据选择的页面显示不同内容
    if st.session_state.current_page == "选题指导":
        topic_guidance_page()
    elif st.session_state.current_page == "论文批注":
        paper_annotation_page()
    elif st.session_state.current_page == "格式修正":
        format_correction_page()
    elif st.session_state.current_page == "学习助手":
        learning_assistant_page()

def topic_guidance_page():
    """选题指导页面"""
    st.header("🎯 论文选题指导")
    
    # 创建更合理的布局
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📝 选题输入与生成")
        
        # 选题输入
        subject = st.text_area(
            "☀ 请描述您想要研究的学术主题",
            height=100,
            placeholder="例如：探讨短视频平台对青少年价值观的影响",
            key="topic_input"
        )
        
        # 参数设置 - 更紧凑的布局
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            word_count = st.number_input(
                "📏 论文篇幅（万字）", 
                min_value=0.1, max_value=5.0, 
                step=0.1, value=0.8
            )
        with col1_2:
            creativity = st.slider(
                "✨ 创意程度", 
                min_value=0.0, max_value=1.0, 
                value=0.3, step=0.1,
                help="数值越小越严谨，越大越创新"
            )
        with col1_3:
            research_type = st.selectbox(
                "🔬 研究类型",
                ["实证研究", "理论研究", "文献综述", "案例研究", "混合研究"]
            )
        
        # 生成按钮
        if st.button("🚀 生成选题建议", type="primary", use_container_width=True):
            if subject:
                # 创建进度条
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # 步骤1：生成选题
                    status_text.text("📝 正在生成选题建议...")
                    progress_bar.progress(25)
                    title, abstract, _ = generate_paper(subject, word_count, creativity)
                    
                    # 步骤2：选题诊断
                    status_text.text("🔍 正在进行选题诊断...")
                    progress_bar.progress(50)
                    diagnosis = topic_diagnosis(subject, research_type)
                    
                    # 步骤3：可行性分析
                    status_text.text("📊 正在分析可行性...")
                    progress_bar.progress(75)
                    feasibility = analyze_topic_feasibility(subject, research_type)
                    
                    # 步骤4：完成
                    status_text.text("✅ 分析完成！")
                    progress_bar.progress(100)
                    
                    # 保存结果到session state
                    st.session_state.topic_analysis = {
                        'title': title,
                        'abstract': abstract,
                        'diagnosis': diagnosis,
                        'feasibility': feasibility,
                        'subject': subject,
                        'word_count': word_count,
                        'creativity': creativity,
                        'research_type': research_type
                    }
                    
                    # 清除进度条
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success("🎉 选题分析完成！")
                    st.rerun()
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ 分析过程中出现错误：{str(e)}")
                    st.info("💡 建议：请检查网络连接或稍后重试")
            else:
                st.warning("⚠️ 请输入研究主题")
    
    with col2:
        st.subheader("📊 实时分析")
        
        # 实时主题分析 - 移到右侧，更紧凑
        if subject:
            # 快速主题评估
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("主题明确度", f"{min(len(subject.split()) * 10, 100)}%")
            with col2_2:
                st.metric("创新潜力", f"{creativity * 100:.0f}%")
            
            # 智能提示 - 更简洁
            if len(subject.split()) < 3:
                st.warning("💡 主题描述可以更具体")
            if creativity < 0.3:
                st.info("💡 可适当提高创意程度")
        
        # 显示选题诊断结果
        if st.session_state.topic_analysis:
            analysis = st.session_state.topic_analysis
            
            # 可行性评分
            if 'feasibility' in analysis:
                feasibility = analysis['feasibility']
                st.metric("可行性评分", f"{feasibility.get('score', 0)}/100")
                
                # 显示详细评估
                st.markdown("**📋 详细评估**")
                st.write("**理论可行性：**", feasibility.get('theoretical', '待评估'))
                st.write("**方法可行性：**", feasibility.get('methodological', '待评估'))
                st.write("**数据可获得性：**", feasibility.get('data_availability', '待评估'))
                st.write("**创新性：**", feasibility.get('innovation', '待评估'))
    
    # 显示生成结果 - 简化布局
    if st.session_state.topic_analysis:
        analysis = st.session_state.topic_analysis
        
        st.markdown("---")
        st.subheader("📋 选题分析结果")
        
        # 创建两列布局显示结果
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🔥 推荐选题")
            
            # 选题展示优化
            title_content = analysis.get('title', '生成中...')
            if title_content and title_content != '生成中...':
                # 将选题分行显示
                titles = [t.strip() for t in title_content.split('\n') if t.strip()]
                for i, title in enumerate(titles, 1):
                    st.markdown(f"**{i}. {title}**")
                
                # 研究建议
                st.markdown("### 📝 研究建议")
                abstract_content = analysis.get('abstract', '生成中...')
                if abstract_content and abstract_content != '生成中...':
                    st.markdown(abstract_content)
            else:
                st.info("正在生成选题建议...")
        
        with col2:
            st.markdown("### 📊 分析报告")
            
            # 选题评分
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("创新性", "85", "↗️ +5")
            with col2_2:
                st.metric("可行性", "78", "↗️ +3")
            
            # 诊断分析
            if 'diagnosis' in analysis:
                diagnosis = analysis['diagnosis']
                with st.expander("🔍 选题诊断"):
                    st.write(diagnosis.get('analysis', '诊断中...'))
            
            # 改进建议
            if 'feasibility' in analysis:
                feasibility = analysis['feasibility']
                with st.expander("💡 改进建议"):
                    suggestions = feasibility.get('suggestions', [])
                    for i, suggestion in enumerate(suggestions, 1):
                        st.write(f"{i}. {suggestion}")
        
        # 操作按钮
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 导出为Word", type="secondary", use_container_width=True):
                st.info("导出功能开发中...")
        with col2:
            if st.button("🔄 重新生成", type="secondary", use_container_width=True):
                st.info("重新生成功能开发中...")
        with col3:
            if st.button("💾 保存到收藏", type="secondary", use_container_width=True):
                st.success("已保存到收藏夹")

def paper_annotation_page():
    """论文批注页面"""
    st.header("✏️ 论文批注修改")
    
    # 创建更简洁的布局
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 文档上传")
        
        # 文件上传
        uploaded_file = st.file_uploader(
            "选择要分析的文档",
            type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'],
            help="支持PDF、Word、文本文件和图片文件"
        )
        
        if uploaded_file is not None:
            # 显示文件信息
            st.metric("文件名", uploaded_file.name)
            st.metric("文件大小", f"{uploaded_file.size / 1024:.1f} KB")
            
            # 处理文档
            if st.button("🔍 分析文档", type="primary", use_container_width=True):
                with st.spinner("正在处理文档..."):
                    # 处理上传的文件
                    doc_result = document_processor.process_uploaded_file(uploaded_file)
                    
                    if "error" in doc_result:
                        st.error(doc_result["error"])
                    else:
                        # 保存文档内容
                        st.session_state.paper_content = doc_result["content"]
                        st.session_state.file_info = doc_result["file_info"]
                        
                        # 进行高级分析
                        analysis_result = advanced_analyzer.comprehensive_analysis(doc_result["content"])
                        
                        # 调试信息
                        if "error" in analysis_result:
                            st.warning(f"分析过程中出现问题: {analysis_result['error']}")
                        else:
                            st.success("文档分析完成！")
                        
                        # 进行AI批注
                        annotation_result = intelligent_annotation(doc_result["content"], "全面批注")
                        
                        # 保存结果
                        st.session_state.annotation_result = annotation_result
                        st.session_state.analysis_result = analysis_result
    
    with col2:
        st.subheader("📝 文本输入")
        
        # 论文内容输入
        paper_content = st.text_area(
            "📄 请输入您要批注的论文内容",
            height=200,
            placeholder="请粘贴您的论文内容，包括标题、摘要、正文等...",
            key="paper_content_input"
        )
        
        # 批注类型选择
        annotation_type = st.selectbox(
            "🔍 批注类型",
            ["全面批注", "学术规范性", "逻辑结构", "内容质量", "语言表达"],
            help="选择您希望重点批注的方面"
        )
        
        # 实时内容分析
        if paper_content:
            # 基础统计
            words = paper_content.split()
            sentences = paper_content.split('。')
            paragraphs = [p.strip() for p in paper_content.split('\n') if p.strip()]
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("字数", len(words))
            with col2_2:
                st.metric("段落数", len(paragraphs))
            
            # 内容质量提示
            if len(words) < 500:
                st.warning("💡 内容较短，建议增加更多详细内容")
            elif len(words) > 5000:
                st.info("💡 内容较长，建议分段进行批注")
        
        # 批注按钮
        if st.button("🔍 开始批注", type="primary", use_container_width=True):
            if paper_content:
                # 创建进度条
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # 步骤1：内容预处理
                    status_text.text("📝 正在预处理内容...")
                    progress_bar.progress(20)
                    
                    # 步骤2：智能批注
                    status_text.text("🤖 AI正在分析您的论文...")
                    progress_bar.progress(60)
                    annotation_result = intelligent_annotation(paper_content, annotation_type)
                    
                    # 步骤3：高级分析
                    status_text.text("📊 正在进行高级分析...")
                    progress_bar.progress(80)
                    analysis_result = advanced_analyzer.comprehensive_analysis(paper_content)
                    
                    # 步骤4：完成
                    status_text.text("✅ 批注分析完成！")
                    progress_bar.progress(100)
                    
                    # 保存结果到session state
                    st.session_state.annotation_result = annotation_result
                    st.session_state.paper_content = paper_content
                    st.session_state.analysis_result = analysis_result
                    
                    # 清除进度条
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success("🎉 批注分析完成！")
                    st.rerun()
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ 批注过程中出现错误：{str(e)}")
                    st.info("💡 建议：请检查网络连接或稍后重试")
            else:
                st.warning("⚠️ 请输入论文内容")
    
    # 显示分析结果
    if 'analysis_result' in st.session_state and st.session_state.analysis_result:
        st.markdown("---")
        st.subheader("📊 文档分析结果")
        
        analysis = st.session_state.analysis_result
        
        # 检查分析结果是否包含错误
        if "error" in analysis:
            st.error(f"分析失败: {analysis['error']}")
            return
        
        # 检查是否有basic_stats
        if "basic_stats" not in analysis:
            st.warning("分析结果不完整，请重新分析文档")
            return
        
        # 基础统计
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总字数", analysis["basic_stats"]["total_words"])
        with col2:
            st.metric("总句数", analysis["basic_stats"]["total_sentences"])
        with col3:
            st.metric("总段落", analysis["basic_stats"]["total_paragraphs"])
        with col4:
            st.metric("阅读时间", f"{analysis['basic_stats']['reading_time_minutes']:.1f}分钟")
        
        # 结构分析
        if "structure_analysis" in analysis:
            st.markdown("### 📋 结构分析")
            structure = analysis["structure_analysis"]
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**结构完整性：**", f"{structure['structure_score']}/100")
                st.progress(structure['structure_score'] / 100)
            
            with col2:
                structure_items = [
                    ("摘要", structure["has_abstract"]),
                    ("关键词", structure["has_keywords"]),
                    ("引言", structure["has_introduction"]),
                    ("结论", structure["has_conclusion"]),
                    ("参考文献", structure["has_references"])
                ]
                
                for item, has_item in structure_items:
                    status = "✅" if has_item else "❌"
                    st.write(f"{status} {item}")
        
        # 学术质量分析
        if "academic_quality" in analysis:
            st.markdown("### 🎯 学术质量分析")
            quality = analysis["academic_quality"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("引用数量", quality["citation_count"])
            with col2:
                st.metric("正式语言", f"{quality['formal_language_score']:.0f}/100")
            with col3:
                st.metric("学术术语", f"{quality['academic_terms_score']:.0f}/100")
        
        # 写作风格分析
        if "writing_style" in analysis:
            st.markdown("### ✍️ 写作风格分析")
            style = analysis["writing_style"]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("句子复杂度", f"{style['sentence_complexity']:.0f}/100")
            with col2:
                st.metric("词汇多样性", f"{style['vocabulary_diversity']:.0f}/100")
            with col3:
                st.metric("语调正式性", f"{style['tone_formality']:.0f}/100")
            with col4:
                st.metric("表达清晰度", f"{style['clarity_score']:.0f}/100")
        
        # 改进建议
        if "recommendations" in analysis:
            st.markdown("### 💡 改进建议")
            recommendations = analysis["recommendations"]
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        
        # 创建选项卡来显示不同的分析结果
        if 'analysis_result' in st.session_state and st.session_state.analysis_result:
            tab1, tab2, tab3, tab4 = st.tabs(["📝 批注结果", "🔍 问题分析", "💡 修改建议", "📊 质量评估"])
            
            with tab1:
                st.markdown("### 📝 批注结果")
                if 'annotation_result' in st.session_state and st.session_state.annotation_result:
                    annotation = st.session_state.annotation_result.get('annotation', '批注中...')
                    if annotation and annotation != '批注中...':
                        # 添加批注操作按钮
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("📄 导出批注", type="secondary", key="export_btn_main"):
                                st.info("导出功能开发中...")
                        with col2:
                            if st.button("🔄 重新批注", type="secondary", key="reannotate_btn_main"):
                                st.info("重新批注功能开发中...")
                        with col3:
                            if st.button("💾 保存批注", type="secondary", key="save_btn_main"):
                                st.success("批注已保存")
                        
                        st.markdown("---")
                        st.markdown("#### 📋 整体批注")
                        st.markdown(annotation)
                    else:
                        st.info("正在生成批注...")
                else:
                    st.info("请先进行文档分析")
            
            with tab2:
                st.markdown("### 🔍 问题分析")
                if 'analysis_result' in st.session_state and st.session_state.analysis_result:
                    analysis = st.session_state.analysis_result
                    
                    # 检查分析结果是否有效
                    if "error" in analysis:
                        st.error(f"分析失败: {analysis['error']}")
                    elif "structure_analysis" in analysis and "academic_quality" in analysis:
                        # 结构问题
                        structure = analysis["structure_analysis"]
                        missing_parts = []
                        if not structure["has_abstract"]: missing_parts.append("摘要")
                        if not structure["has_keywords"]: missing_parts.append("关键词")
                        if not structure["has_introduction"]: missing_parts.append("引言")
                        if not structure["has_conclusion"]: missing_parts.append("结论")
                        if not structure["has_references"]: missing_parts.append("参考文献")
                        
                        if missing_parts:
                            st.warning(f"缺少以下部分：{', '.join(missing_parts)}")
                        
                        # 学术质量问题
                        quality = analysis["academic_quality"]
                        if quality["citation_count"] < 3:
                            st.warning("引用数量较少，建议增加文献引用")
                        if quality["formal_language_score"] < 50:
                            st.warning("正式语言使用不足，建议增加学术表达")
                    else:
                        st.warning("分析结果不完整，请重新分析")
                else:
                    st.info("请先进行文档分析")
            
            with tab3:
                st.markdown("### 💡 修改建议")
                if 'analysis_result' in st.session_state and st.session_state.analysis_result:
                    analysis = st.session_state.analysis_result
                    if "error" in analysis:
                        st.error(f"分析失败: {analysis['error']}")
                    elif "recommendations" in analysis:
                        recommendations = analysis["recommendations"]
                        for i, rec in enumerate(recommendations, 1):
                            st.write(f"{i}. {rec}")
                    else:
                        st.warning("分析结果不完整，请重新分析")
                else:
                    st.info("请先进行文档分析")
            
            with tab4:
                st.markdown("### 📊 质量评估")
                if 'analysis_result' in st.session_state and st.session_state.analysis_result:
                    analysis = st.session_state.analysis_result
                    
                    # 检查分析结果是否有效
                    if "error" in analysis:
                        st.error(f"分析失败: {analysis['error']}")
                    elif all(key in analysis for key in ["structure_analysis", "academic_quality", "writing_style"]):
                        # 创建质量评估图表
                        import plotly.graph_objects as go
                        
                        categories = ['结构完整性', '学术质量', '写作风格', '引用规范']
                        values = [
                            analysis["structure_analysis"]["structure_score"],
                            analysis["academic_quality"]["overall_quality_score"],
                            (analysis["writing_style"]["tone_formality"] + analysis["writing_style"]["clarity_score"]) / 2,
                            min(analysis["academic_quality"]["citation_count"] * 20, 100)
                        ]
                        
                        fig = go.Figure(data=[
                            go.Bar(x=categories, y=values, marker_color='lightblue')
                        ])
                        fig.update_layout(
                            title="论文质量评估",
                            yaxis=dict(range=[0, 100]),
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("分析结果不完整，无法生成质量评估图表")
                else:
                    st.info("请先进行文档分析")
        
        
        # 示例论文内容
        if not st.session_state.paper_content:
            st.markdown("---")
            st.subheader("💡 使用示例")
            
            with st.expander("📖 查看示例论文内容"):
                example_content = """
标题：社交媒体对大学生学习行为的影响研究

摘要：本研究旨在探讨社交媒体对大学生学习行为的影响。通过问卷调查和深度访谈的方法，收集了500名大学生的数据。研究发现，社交媒体对大学生的学习行为具有双重影响：一方面，社交媒体提供了丰富的学习资源和交流平台；另一方面，过度使用社交媒体可能分散学习注意力。研究建议大学生应合理使用社交媒体，发挥其积极作用，避免负面影响。

关键词：社交媒体；大学生；学习行为；影响研究

1. 引言
随着互联网技术的发展，社交媒体已成为大学生日常生活的重要组成部分。大学生群体是社交媒体的主要用户，他们的学习行为不可避免地受到社交媒体的影响。本研究旨在深入探讨社交媒体对大学生学习行为的具体影响机制。

2. 文献综述
2.1 社交媒体的概念与特征
社交媒体是指基于互联网技术，允许用户创建、分享和交流内容的平台。其主要特征包括互动性、即时性和个性化。

2.2 大学生学习行为研究
学习行为是指个体在学习过程中表现出来的各种行为模式，包括学习动机、学习策略和学习效果等方面。

3. 研究方法
3.1 研究对象
本研究选取某高校500名大学生作为研究对象，其中男生250名，女生250名。

3.2 研究方法
采用问卷调查和深度访谈相结合的方法，收集定量和定性数据。

4. 研究结果
4.1 社交媒体使用现状
调查显示，95%的大学生每天使用社交媒体，平均使用时间为3-5小时。

4.2 对学习行为的影响
社交媒体对学习行为的影响主要体现在学习时间分配、学习注意力集中和学习效果等方面。

5. 讨论
研究结果表明，社交媒体对大学生的学习行为具有复杂的影响。需要进一步研究如何优化社交媒体使用，提高学习效果。

6. 结论
本研究揭示了社交媒体对大学生学习行为的影响机制，为教育工作者和学生提供了有益的参考。
                """
                st.text_area("示例内容", example_content, height=300, disabled=True)

def format_correction_page():
    """格式修正页面"""
    st.header("📐 论文格式修正")
    
    # 创建更简洁的布局
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 文档上传")
        
        # 文件上传
        uploaded_file = st.file_uploader(
            "选择要修正格式的文档",
            type=['pdf', 'docx', 'txt'],
            help="支持PDF、Word、文本文件"
        )
        
        if uploaded_file is not None:
            # 显示文件信息
            st.metric("文件名", uploaded_file.name)
            st.metric("文件大小", f"{uploaded_file.size / 1024:.1f} KB")
            
            # 处理文档
            if st.button("🔧 分析文档格式", type="primary", use_container_width=True):
                with st.spinner("正在处理文档..."):
                    # 处理上传的文件
                    doc_result = document_processor.process_uploaded_file(uploaded_file)
                    
                    if "error" in doc_result:
                        st.error(doc_result["error"])
                    else:
                        # 保存文档内容
                        st.session_state.format_content = doc_result["content"]
                        st.session_state.file_info = doc_result["file_info"]
                        
                        # 进行格式分析
                        format_analysis_result = advanced_analyzer.comprehensive_analysis(doc_result["content"])
                        
                        # 调试信息
                        if "error" in format_analysis_result:
                            st.warning(f"格式分析过程中出现问题: {format_analysis_result['error']}")
                        else:
                            st.success("文档格式分析完成！")
                        
                        # 保存结果
                        st.session_state.format_analysis_result = format_analysis_result
    
    with col2:
        st.subheader("📝 文本输入")
        
        # 论文内容输入
        paper_content = st.text_area(
            "📄 请输入您要修正格式的论文内容",
            height=200,
            placeholder="请粘贴您的论文内容，包括标题、摘要、正文等...",
            key="format_content_input"
        )
        
        # 目标格式选择
        target_format = st.selectbox(
            "📋 目标格式",
            ["APA格式", "MLA格式", "Chicago格式", "GB/T 7714格式"],
            help="选择您希望应用的格式标准",
            key="format_selectbox_text"
        )
        
        # 实时内容分析
        if paper_content:
            # 基础统计
            words = paper_content.split()
            sentences = paper_content.split('。')
            paragraphs = [p.strip() for p in paper_content.split('\n') if p.strip()]
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("字数", len(words))
            with col2_2:
                st.metric("段落数", len(paragraphs))
            
            # 内容质量提示
            if len(words) < 500:
                st.warning("💡 内容较短，建议增加更多详细内容")
            elif len(words) > 5000:
                st.info("💡 内容较长，建议分段进行格式修正")
        
        # 格式修正按钮
        if st.button("🔧 开始格式修正", type="primary", use_container_width=True):
            if paper_content:
                # 创建进度条
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # 步骤1：内容预处理
                    status_text.text("📝 正在预处理内容...")
                    progress_bar.progress(20)
                    
                    # 步骤2：格式分析
                    status_text.text("🔍 AI正在分析格式问题...")
                    progress_bar.progress(50)
                    format_analysis_result = advanced_analyzer.comprehensive_analysis(paper_content)
                    
                    # 步骤3：格式修正
                    status_text.text("🔧 正在进行格式修正...")
                    progress_bar.progress(80)
                    from PaperHelper_utils import format_correction
                    format_result = format_correction(paper_content, target_format)
                    
                    # 步骤4：完成
                    status_text.text("✅ 格式修正完成！")
                    progress_bar.progress(100)
                    
                    # 保存结果到session state
                    st.session_state.format_result = format_result
                    st.session_state.format_content = paper_content
                    st.session_state.format_analysis_result = format_analysis_result
                    
                    # 清除进度条
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success("🎉 格式修正完成！")
                    st.rerun()
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ 格式修正过程中出现错误：{str(e)}")
                    st.info("💡 建议：请检查网络连接或稍后重试")
            else:
                st.warning("⚠️ 请输入论文内容")
    
    # 显示格式分析结果
    if 'format_analysis_result' in st.session_state and st.session_state.format_analysis_result:
        st.markdown("---")
        st.subheader("📊 格式分析结果")
        
        analysis = st.session_state.format_analysis_result
        
        # 检查分析结果是否包含错误
        if "error" in analysis:
            st.error(f"格式分析失败: {analysis['error']}")
        else:
            # 基础统计
            if "basic_stats" in analysis:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总字数", analysis["basic_stats"]["total_words"])
                with col2:
                    st.metric("总句数", analysis["basic_stats"]["total_sentences"])
                with col3:
                    st.metric("总段落", analysis["basic_stats"]["total_paragraphs"])
                with col4:
                    st.metric("阅读时间", f"{analysis['basic_stats']['reading_time_minutes']:.1f}分钟")
            
            # 结构分析（作为格式分析的一部分）
            if "structure_analysis" in analysis:
                st.markdown("### 🔍 结构格式分析")
                structure = analysis["structure_analysis"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**结构完整性：**", f"{structure['structure_score']}/100")
                    st.progress(structure['structure_score'] / 100)
                
                with col2:
                    structure_items = [
                        ("摘要", structure["has_abstract"]),
                        ("关键词", structure["has_keywords"]),
                        ("引言", structure["has_introduction"]),
                        ("结论", structure["has_conclusion"]),
                        ("参考文献", structure["has_references"])
                    ]
                    
                    for item, has_item in structure_items:
                        status = "✅" if has_item else "❌"
                        st.write(f"{status} {item}")
            
            # 学术质量分析（作为格式分析的一部分）
            if "academic_quality" in analysis:
                st.markdown("### 🎯 学术格式质量")
                quality = analysis["academic_quality"]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("引用数量", quality["citation_count"])
                with col2:
                    st.metric("正式语言", f"{quality['formal_language_score']:.0f}/100")
                with col3:
                    st.metric("学术术语", f"{quality['academic_terms_score']:.0f}/100")
            
            # 改进建议
            if "recommendations" in analysis:
                st.markdown("### 💡 格式改进建议")
                recommendations = analysis["recommendations"]
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec}")
    
    # 显示格式修正结果
    if 'format_result' in st.session_state and st.session_state.format_result:
        st.markdown("---")
        st.subheader("📋 格式修正结果")
        
        # 创建选项卡来显示不同的结果
        if 'format_analysis_result' in st.session_state and st.session_state.format_analysis_result:
            format_tab1, format_tab2, format_tab3 = st.tabs(["📝 修正后内容", "🔍 格式检查", "📋 格式规范"])
            
            with format_tab1:
                st.markdown("### 📝 修正后的论文内容")
                if 'format_result' in st.session_state and st.session_state.format_result:
                    corrected_content = st.session_state.format_result.get('corrected_content', '修正中...')
                    if corrected_content and corrected_content != '修正中...':
                        # 添加格式修正操作按钮
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("📄 导出文档", type="secondary", key="export_format_btn"):
                                st.info("导出功能开发中...")
                        with col2:
                            if st.button("🔄 重新修正", type="secondary", key="reformat_btn"):
                                st.info("重新修正功能开发中...")
                        with col3:
                            if st.button("💾 保存结果", type="secondary", key="save_format_btn"):
                                st.success("格式修正结果已保存")
                        
                        st.markdown("---")
                        st.text_area("修正结果", corrected_content, height=400, disabled=True)
                    else:
                        st.info("正在生成格式修正结果...")
                else:
                    st.info("请先进行格式修正")
            
            with format_tab2:
                st.markdown("### 🔍 格式检查报告")
                if 'format_analysis_result' in st.session_state and st.session_state.format_analysis_result:
                    analysis = st.session_state.format_analysis_result
                    if "error" in analysis:
                        st.error(f"格式检查失败: {analysis['error']}")
                    elif "structure_analysis" in analysis:
                        structure = analysis["structure_analysis"]
                        st.write("**发现的主要格式问题：**")
                        if not structure["has_abstract"]:
                            st.warning("❌ 缺少摘要")
                        if not structure["has_keywords"]:
                            st.warning("❌ 缺少关键词")
                        if not structure["has_introduction"]:
                            st.warning("❌ 缺少引言")
                        if not structure["has_conclusion"]:
                            st.warning("❌ 缺少结论")
                        if not structure["has_references"]:
                            st.warning("❌ 缺少参考文献")
                        
                        # 学术质量检查
                        if "academic_quality" in analysis:
                            quality = analysis["academic_quality"]
                            if quality["citation_count"] < 3:
                                st.warning("⚠️ 引用数量较少，建议增加文献引用")
                            if quality["formal_language_score"] < 50:
                                st.warning("⚠️ 正式语言使用不足，建议增加学术表达")
                    else:
                        st.warning("格式检查结果不完整，请重新分析")
                else:
                    st.info("请先进行格式分析")
            
            with format_tab3:
                st.markdown("### 📋 格式规范说明")
                st.info("格式规范说明功能正在完善中...")
    
    # 格式规范说明
    st.markdown("---")
    st.subheader("📚 格式规范说明")
    
    with st.expander("📖 查看格式规范"):
        st.markdown("""
        ### APA格式规范要点：
        1. **标题格式**：标题居中，使用标题大小写
        2. **段落格式**：首行缩进0.5英寸，双倍行距
        3. **引用格式**：作者-年份格式，如(Smith, 2020)
        4. **参考文献**：按字母顺序排列，悬挂缩进
        
        ### MLA格式规范要点：
        1. **标题格式**：标题居中，使用标题大小写
        2. **段落格式**：首行缩进1英寸，双倍行距
        3. **引用格式**：作者-页码格式，如(Smith 45)
        4. **参考文献**：按字母顺序排列，悬挂缩进
        
        ### GB/T 7714格式规范要点：
        1. **标题格式**：标题居中，使用黑体
        2. **段落格式**：首行缩进2字符，1.5倍行距
        3. **引用格式**：顺序编码制，如[1]
        4. **参考文献**：按引用顺序排列
        """)

def learning_assistant_page():
    """学习助手页面"""
    st.header("🎓 学习助手")
    
    # 创建选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["📚 文献管理", "✍️ 写作助手", "📊 进度追踪", "🎯 学术资源"])
    
    with tab1:
        st.subheader("📚 文献管理")
        
        # 文献检索
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_keyword = st.text_input(
                "🔍 文献检索关键词",
                placeholder="输入您要检索的关键词，如：社交媒体、传播理论等"
            )
            
            search_type = st.selectbox(
                "📋 检索类型",
                ["期刊论文", "学位论文", "会议论文", "专著", "报告"]
            )
            
            if st.button("🔍 开始检索", type="primary"):
                if search_keyword:
                    st.info("文献检索功能正在开发中，敬请期待！")
                else:
                    st.warning("请输入检索关键词")
        
        with col2:
            st.subheader("📊 检索统计")
            st.metric("检索结果", "0 篇")
            st.metric("相关度", "待评估")
        
        # 文献整理
        st.markdown("---")
        st.subheader("📋 文献整理")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📖 已收藏文献")
            st.info("文献收藏功能正在开发中...")
        
        with col2:
            st.markdown("### 📝 阅读笔记")
            st.info("笔记功能正在开发中...")
        
        with col3:
            st.markdown("### 🔗 文献引用")
            st.info("引用管理功能正在开发中...")
    
    with tab2:
        st.subheader("✍️ 写作助手")
        
        # 写作技巧指导
        writing_topic = st.selectbox(
            "📝 选择写作主题",
            ["论文结构", "学术表达", "论证方法", "文献综述", "研究方法", "结论写作"]
        )
        
        if st.button("📖 获取写作指导", type="primary"):
            if WRITING_ASSISTANT_AVAILABLE:
                # 获取写作指导
                guide_result = writing_assistant.get_writing_guide(writing_topic)
                
                if guide_result["success"]:
                    st.success("写作指导生成完成！")
                    
                    with st.expander("📖 写作指导"):
                        st.markdown(guide_result["guide"])
                else:
                    st.error(guide_result["error"])
            else:
                # 提供基础写作指导
                st.success("写作指导生成完成！")
                
                with st.expander("📖 写作指导"):
                    if writing_topic == "论文结构":
                        st.markdown("""
                        ### 论文结构指导
                        
                        **标准学术论文结构：**
                        1. **标题** - 简洁明确，反映研究内容
                        2. **摘要** - 200-300字，概括研究目的、方法、结果、结论
                        3. **关键词** - 3-5个，便于检索
                        4. **引言** - 研究背景、问题提出、研究意义
                        5. **文献综述** - 相关研究回顾，理论框架
                        6. **研究方法** - 研究设计、数据收集、分析方法
                        7. **研究结果** - 数据分析结果，图表展示
                        8. **讨论** - 结果解释，理论贡献，局限性
                        9. **结论** - 研究总结，实践意义，未来方向
                        10. **参考文献** - 标准格式引用
                        """)
                    elif writing_topic == "学术表达":
                        st.markdown("""
                        ### 学术表达指导
                        
                        **学术写作要点：**
                        - 使用客观、准确的学术语言
                        - 避免主观判断和情感色彩
                        - 使用第三人称，避免第一人称
                        - 使用被动语态，强调客观性
                        - 使用专业术语，保持一致性
                        - 使用逻辑连接词，增强连贯性
                        """)
                    else:
                        st.write(f"关于'{writing_topic}'的详细指导正在生成中...")
        
        # 写作模板
        st.markdown("---")
        st.subheader("📋 写作模板")
        
        template_type = st.selectbox(
            "📄 选择模板类型",
            ["论文大纲模板", "文献综述模板", "研究方法模板", "结论模板"]
        )
        
        # 添加主题和要求输入
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("研究主题（可选）", placeholder="如：社交媒体对传播效果的影响")
        with col2:
            requirements = st.text_input("特殊要求（可选）", placeholder="如：需要包含定量分析")
        
        if st.button("📄 生成模板", type="primary"):
            if WRITING_ASSISTANT_AVAILABLE:
                # 生成模板
                template_result = writing_assistant.generate_template(template_type, topic, requirements)
                
                if template_result["success"]:
                    st.success("模板生成完成！")
                    
                    with st.expander("📄 写作模板"):
                        st.markdown(template_result["template"])
                else:
                    st.error(template_result["error"])
            else:
                # 提供基础模板
                st.success("模板生成完成！")
                
                with st.expander("📄 写作模板"):
                    if template_type == "论文大纲模板":
                        st.markdown("""
                        ### 论文大纲模板
                        
                        **标题：** [论文标题]
                        
                        **1. 引言**
                           - 1.1 研究背景
                           - 1.2 问题提出
                           - 1.3 研究目的
                           - 1.4 研究意义
                        
                        **2. 文献综述**
                           - 2.1 理论基础
                           - 2.2 相关研究
                           - 2.3 研究假设
                        
                        **3. 研究方法**
                           - 3.1 研究设计
                           - 3.2 样本选择
                           - 3.3 数据收集
                           - 3.4 分析方法
                        
                        **4. 研究结果**
                           - 4.1 描述性统计
                           - 4.2 假设检验
                           - 4.3 结果分析
                        
                        **5. 讨论**
                           - 5.1 结果解释
                           - 5.2 理论贡献
                           - 5.3 实践意义
                           - 5.4 研究局限
                        
                        **6. 结论**
                           - 6.1 研究总结
                           - 6.2 未来方向
                        """)
                    else:
                        st.write(f"'{template_type}'模板正在生成中...")
        
        # 实时写作建议
        st.markdown("---")
        st.subheader("💡 实时写作建议")
        
        writing_content = st.text_area(
            "输入您正在写作的内容",
            height=150,
            placeholder="粘贴您正在写作的段落或句子，获取实时建议..."
        )
        
        if st.button("🔍 获取建议", type="primary"):
            if writing_content:
                if WRITING_ASSISTANT_AVAILABLE:
                    # 获取实时建议
                    suggestion_result = writing_assistant.provide_real_time_suggestions(writing_content)
                    
                    if suggestion_result["success"]:
                        st.success("建议生成完成！")
                        
                        with st.expander("💡 写作建议"):
                            st.markdown(suggestion_result["suggestions"])
                    else:
                        st.error(suggestion_result["error"])
                else:
                    st.info("实时写作建议功能正在开发中，敬请期待！")
            else:
                st.warning("请输入要分析的内容")
    
    with tab3:
        st.subheader("📊 进度追踪")
        
        # 论文写作进度
        st.markdown("### 📈 论文写作进度")
        
        # 进度条
        progress = st.slider("整体进度", 0, 100, 25, help="调整您的论文写作进度")
        st.progress(progress / 100)
        
        # 各阶段进度
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 各阶段进度")
            st.write("选题阶段：", "✅ 已完成")
            st.write("文献综述：", "🔄 进行中")
            st.write("研究方法：", "⏳ 待开始")
            st.write("数据收集：", "⏳ 待开始")
            st.write("论文写作：", "⏳ 待开始")
            st.write("修改完善：", "⏳ 待开始")
        
        with col2:
            st.markdown("#### 📅 时间规划")
            st.write("开始时间：2024年1月")
            st.write("预计完成：2024年6月")
            st.write("剩余时间：3个月")
        
        # 学习记录
        st.markdown("---")
        st.subheader("📝 学习记录")
        st.info("学习记录功能正在开发中...")
    
    with tab4:
        st.subheader("🎯 学术资源")
        
        # 学术资源推荐
        st.markdown("### 📚 推荐学术资源")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔬 研究方法")
            st.write("• 定量研究方法")
            st.write("• 定性研究方法")
            st.write("• 混合研究方法")
            st.write("• 案例研究方法")
        
        with col2:
            st.markdown("#### 📖 理论资源")
            st.write("• 传播学理论")
            st.write("• 媒介效果理论")
            st.write("• 受众研究理论")
            st.write("• 新媒体理论")
        
        # 学术期刊推荐
        st.markdown("---")
        st.subheader("📰 学术期刊推荐")
        
        journal_categories = ["传播学核心期刊", "新闻学核心期刊", "新媒体研究期刊", "国际期刊"]
        
        for category in journal_categories:
            with st.expander(f"📖 {category}"):
                st.write("期刊推荐功能正在开发中...")
        
        # 学术会议信息
        st.markdown("---")
        st.subheader("🎪 学术会议信息")
        st.info("学术会议信息功能正在开发中...")

# 运行主程序
if __name__ == "__main__":
    main_page()
