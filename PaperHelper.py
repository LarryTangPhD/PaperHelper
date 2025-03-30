import streamlit as st
from PaperHelper_utils import generate_paper

st.title("💡 新传论文创意生成器")


subject = st.text_area("☀ 请简单描述你想要进行学术探索的大致主题", 
                      height=100,
                      placeholder="例如：探讨短视频平台对青少年价值观的影响")
word_count = st.number_input("⏱️ 请输入最终撰写论文的大致篇幅（单位：万字）", min_value=0.1,max_value=3.0, step=0.1, value=0.8)
creativity = st.slider("✨ 请输入论文创意的创造力（数字小说明更严谨，数字大说明更富有创意）", min_value=0.0,
                       max_value=1.0, value=0.2, step=0.1)
submit = st.button("生成论文创意")


if submit and not subject:
    st.info("请输入初步的研究创意")
    st.stop()
if submit and not word_count >= 0.1:
    st.info("成文应具有一定的篇幅")
    st.stop()
if submit:
    with st.spinner("AI正在思考中，请稍后...（调用deepseek大模型，思考越久，结果越好）"):
        title, abstract, _ = generate_paper(subject, word_count, creativity)
    st.success("论文创意已生成！")
    st.subheader("🔥 标题：")
    st.write(title)
    st.subheader("📝 研究建议：")
    st.write(abstract)

# 加入一个侧边栏，阐述作者个人信息与项目基本情况
# 在侧边栏中创建内容
with st.sidebar:
    # 添加总抬头
    st.header("✒ 新传青登工作室")
    
    # 添加作者图片
    st.image("作者头像.jpeg", width=200)
    
    # 添加介绍性文字
    st.markdown("""
    ### 工具介绍
    - 专为新闻传播学研究者打造的论文创意智能生成器，助您突破思维瓶颈，激发研究灵感
    - 只需输入您想要研究的大致学术主题（新闻传播方向），AI将为您量身定制多个创新性论文选题，并提供详细的研究框架建议
    - 支持个性化设置：自由调节论文篇幅（0.1-3万字）和创意程度（严谨↔创新），满足不同研究需求

    ### 技术亮点
    - 基于DeepSeek大语言模型，采用先进的小样本提示词（Few-shot Prompting）技术
    - 严格遵循新闻传播学学术规范，确保生成内容专业可靠
    - 智能优化提示词工程，持续提升生成质量与准确性

    ### 温馨提示
    - 由于深度计算需求，当前的回答生成过程可能需要约2分钟，请耐心等待
    - 我们正在持续优化系统性能，未来将提供更快的响应速度
    """)
