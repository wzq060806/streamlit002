import streamlit as st
import random
import time

# =========================================================
# MBTI 专业人格测试系统 —— 卡片精美版
# 功能：首页选择测试版本 → 随机抽取题目 → 答题计分 → 生成人格结果
# =========================================================

# ===================== 页面全局配置 =====================
st.set_page_config(
    page_title="🔮 MBTI 人格测试",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== 全局样式美化 =====================
st.markdown("""
<style>
/* 页面整体背景渐变 */
.stApp {
    background: linear-gradient(135deg, #e8f0fe 0%, #f5f9ff 100%);
}

/* 内容区域宽度限制，保证居中美观 */
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* 测试版本选择卡片基础样式 */
.version-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 28px 20px;
    text-align: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    border: 2px solid transparent;
    transition: all 0.3s ease;
    height: 100%;
}

/* 选中状态的卡片样式 */
.version-card.active {
    border-color: #1976d2;
    background-color: #e3f2fd;
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(25, 118, 210, 0.12);
}

/* 鼠标悬浮卡片效果 */
.version-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(25, 118, 210, 0.12);
}

/* 卡片图标、标题、描述样式 */
.card-icon {
    font-size: 50px;
    margin-bottom: 12px;
}
.card-title {
    font-size: 22px;
    font-weight: bold;
    color: #222;
    margin: 0;
}
.card-desc {
    font-size: 15px;
    color: #666;
    margin-top: 4px;
}

/* 按钮样式美化 */
.stButton>button {
    border-radius: 12px;
    height: 54px;
    font-size: 18px;
    font-weight: 500;
}

/* 隐藏系统默认菜单、页脚、头部 */
#MainMenu, footer, header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# ===================== 导入外部题库资源 =====================
# 题库、答案、计分规则、人格名称、人格描述均从外部文件导入
from Q_mbti3 import question_file, answer_file, score_map, mbti_names, mbti_descriptions

# ===================== 会话状态初始化 =====================
# 初始化页面路由、测试版本、题目列表、总题数
if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "test_version" not in st.session_state:
    st.session_state["test_version"] = None
if "question_keys" not in st.session_state:
    st.session_state["question_keys"] = None
if "total_questions" not in st.session_state:
    st.session_state["total_questions"] = 0


# ===================== 页面路由函数 =====================
def go_to_home():
    """返回首页，重置所有测试相关状态"""
    st.session_state["page"] = "home"
    st.session_state["test_version"] = None
    st.session_state["question_keys"] = None
    st.session_state["total_questions"] = 0
    st.rerun()


def go_to_test():
    """跳转到测试答题页面"""
    st.session_state["page"] = "test"
    st.rerun()


def go_to_result():
    """跳转到结果展示页面"""
    st.session_state["page"] = "result"
    st.rerun()


def show_loading_animation():
    """结果加载动画：进度条 + 文字提示，提升用户体验"""
    loading_text = st.empty()
    progress_bar = st.progress(0)
    loading_text.info("正在匹配你的人格类型...")
    for i in range(101):
        progress_bar.progress(i)
        time.sleep(0.03)
    time.sleep(0.4)
    loading_text.empty()
    progress_bar.empty()


# ===================== 页面一：测试首页 =====================
# 功能：展示标题、选择测试版本、开始测试
if st.session_state["page"] == "home":
    # 页面标题区域
    st.markdown("""
    <div style="text-align:center; margin:30px 0 40px;">
        <div style="font-size:60px;">🔮</div>
        <h1 style="font-weight:600; margin:10px 0 6px;">MBTI 人格专业测试</h1>
        <p style="font-size:17px; color:#555;">根据真实想法选择，题目无对错，了解真实的自己</p>
    </div>
    """, unsafe_allow_html=True)

    # 版本选择标题
    st.markdown(
        "<div style='margin-bottom:30px;'><h3 style='text-align:center; font-weight:500;'>选择测试版本</h3></div>",
        unsafe_allow_html=True)

    # 隐藏原生单选框，仅使用卡片交互
    st.markdown("""
    <style>
    .stRadio[role="radiogroup"] {
        position: absolute;
        opacity: 0;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # 版本选择单选框（隐藏状态）
    selected_version = st.radio(
        "",
        ["极速版（16题）", "标准版（93题）", "专业版（128题）"],
        horizontal=True,
        label_visibility="collapsed",
        index=0
    )

    # 三列布局：展示三个测试版本卡片
    col_left, col_mid, col_right = st.columns([1, 1, 1])

    with col_left:
        active = "active" if selected_version == "极速版（16题）" else ""
        st.markdown(f"""<div class="version-card {active}">
            <div class="card-icon">⚡</div>
            <p class="card-title">极速版</p>
            <p class="card-desc">16 题 · 快速测试</p>
        </div>""", unsafe_allow_html=True)

    with col_mid:
        active = "active" if selected_version == "标准版（93题）" else ""
        st.markdown(f"""<div class="version-card {active}">
            <div class="card-icon">📘</div>
            <p class="card-title">标准版</p>
            <p class="card-desc">93 题 · 准确平衡</p>
        </div>""", unsafe_allow_html=True)

    with col_right:
        active = "active" if selected_version == "专业版（128题）" else ""
        st.markdown(f"""<div class="version-card {active}">
            <div class="card-icon">📚</div>
            <p class="card-title">专业版</p>
            <p class="card-desc">128 题 · 深度解析</p>
        </div>""", unsafe_allow_html=True)

    # 开始测试按钮
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    if st.button("🚀 开始测试", use_container_width=True, type="secondary"):
        # 保存选择的测试版本
        st.session_state["test_version"] = selected_version

        # 按维度分类题目
        questions_by_dim = {}
        for key, question in question_file.items():
            dim = key.split("_")[0]
            if dim not in questions_by_dim:
                questions_by_dim[dim] = []
            questions_by_dim[dim].append(key)

        # 匹配版本对应的总题数
        version_info = {
            "极速版（16题）": 16,
            "标准版（93题）": 93,
            "专业版（128题）": 128
        }
        total_questions = version_info[selected_version]

        # 均匀分配各维度题目数量
        dims = list(questions_by_dim.keys())
        dim_count = len(dims)
        questions_per_dim = total_questions // dim_count
        remaining = total_questions % dim_count

        # 随机抽取题目
        selected_questions = []
        for i, (dim, qs) in enumerate(questions_by_dim.items()):
            cnt = questions_per_dim + (1 if i < remaining else 0)
            sel = random.sample(qs, min(cnt, len(qs)))
            selected_questions += sel

        # 打乱题目顺序并保存到会话
        random.shuffle(selected_questions)
        st.session_state["question_keys"] = selected_questions
        st.session_state["total_questions"] = len(selected_questions)

        # 跳转到测试页面
        go_to_test()

# ===================== 页面二：测试答题页面 =====================
# 功能：展示题目、收集答案、提交计分
elif st.session_state["page"] == "test":
    # 顶部版本与题数提示栏
    st.markdown(f"""
    <div style="text-align:center; margin:10px 0; padding:12px; background:#e3f2fd; border-radius:10px;">
        <p style="color:#1976d2; font-weight:bold;">
            当前版本：{st.session_state["test_version"]} | 共 {st.session_state["total_questions"]} 题
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 答题容器
    answers = {}
    st.markdown('<div style="max-width:800px; margin:0 auto;">', unsafe_allow_html=True)

    # 循环渲染所有题目
    for key in st.session_state["question_keys"]:
        ans = st.radio(
            question_file[key],
            options=answer_file,
            horizontal=True
        )
        answers[key] = ans

    # 底部操作按钮：返回首页 / 完成答题
    col1, col2 = st.columns(2)
    with col1:
        if st.button("返回首页", use_container_width=True):
            go_to_home()
    with col2:
        submit_btn = st.button("✅ 完成答题，查看结果", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 提交答案，计算人格结果
    if submit_btn:
        show_loading_animation()

        # 初始化各维度分数
        E = I = S = N = T = F = J = P = 0

        # 遍历答案计分
        for key in answers:
            dim = key.split("_")[0]
            s = score_map[answers[key]]
            if dim == "E": E += s
            if dim == "I": I += s
            if dim == "S": S += s
            if dim == "N": N += s
            if dim == "T": T += s
            if dim == "F": F += s
            if dim == "J": J += s
            if dim == "P": P += s

        # 判断最终人格类型
        ei = "E" if E > I else "I"
        sn = "S" if S > N else "N"
        tf = "T" if T > F else "F"
        jp = "J" if J > P else "P"
        mbti = ei + sn + tf + jp

        # 保存结果到会话
        st.session_state["mbti"] = mbti
        st.session_state["answers"] = answers

        # 跳转到结果页面
        go_to_result()

# ===================== 页面三：测试结果页面 =====================
# 功能：展示人格类型、描述、优势、劣势、适合职业
elif st.session_state["page"] == "result":
    mbti = st.session_state["mbti"]

    # 结果展示标题区域
    st.markdown(f"""
    <div style="text-align:center; margin:30px 0;">
        <h3 style="color:#1976d2;">🎉 你的人格已匹配完成</h3>
        <h1 style="color:#1565c0; font-size:52px; font-weight:bold;">{mbti}</h1>
        <h2 style="color:#333;">{mbti_names[mbti]}</h2>
    </div>
    """, unsafe_allow_html=True)

    # 庆祝动画
    st.balloons()

    # 获取人格详细信息
    data = mbti_descriptions.get(mbti, {})

    # 展示详细解析
    if 'description' in data:
        st.markdown(f"**📝 人格描述：** {data['description']}")
    if 'strengths' in data:
        st.markdown(f"**✅ 优势：** {', '.join(data['strengths'])}")
    if 'weaknesses' in data:
        st.markdown(f"**⚠️ 劣势：** {', '.join(data['weaknesses'])}")
    if 'careers' in data:
        st.markdown(f"**💼 适合职业：** {', '.join(data['careers'])}")

    # 结果提示框
    st.success(f"最终人格类型：【{mbti}】{mbti_names[mbti]}")

    # 重新测试按钮
    if st.button("🔁 返回首页重新测试", use_container_width=True):
        go_to_home()