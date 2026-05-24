# hotel_booking_experiment_app.py
# 酒店预订实验模拟系统 V3
# 重点升级：
# 1. 不再像PPT翻页，而是通过页面内真实按钮推进流程
# 2. 房型选择、公益加购、取消公益、确认订单、模拟支付都有真实交互
# 3. 公益产品购买状态会在订单确认页和支付页持续显示
# 4. 保留星级酒店官网模式 + 中国OTA App模式
#
# 运行方式：
# python -m streamlit run hotel_booking_experiment_app.py

import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, date, timedelta

# =====================================================
# 0. 页面配置
# =====================================================
st.set_page_config(
    page_title="酒店预订实验模拟系统",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# 1. CSS 美化
# =====================================================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 4px 18px 4px;
        border-bottom: 1px solid #e7e2dc;
        margin-bottom: 18px;
    }
    .brand-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #2b2118;
    }
    .brand-subtitle {
        font-size: 13px;
        color: #766a60;
        margin-top: -4px;
    }
    .nav-item {
        display: inline-block;
        margin-left: 22px;
        color: #4d4036;
        font-size: 14px;
    }
    .hero {
        min-height: 310px;
        border-radius: 18px;
        padding: 44px;
        color: white;
        background: linear-gradient(90deg, rgba(32,24,19,0.78), rgba(32,24,19,0.28)),
                    url('https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1600');
        background-size: cover;
        background-position: center;
        box-shadow: 0 10px 35px rgba(0,0,0,0.12);
        margin-bottom: 20px;
    }
    .hero h1 {
        font-size: 42px;
        margin-bottom: 8px;
        line-height: 1.15;
    }
    .hero p {
        font-size: 17px;
        max-width: 620px;
        color: rgba(255,255,255,0.92);
    }
    .search-box {
        background: #ffffff;
        border: 1px solid #ebe5dd;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.08);
        margin-top: -34px;
        margin-bottom: 22px;
        position: relative;
        z-index: 5;
    }
    .lux-card {
        background: #ffffff;
        border: 1px solid #eee6df;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 6px 20px rgba(35,24,16,0.06);
        margin-bottom: 16px;
    }
    .room-card {
        border: 1px solid #e8dfd6;
        border-radius: 16px;
        padding: 18px;
        background: #fff;
        margin-bottom: 14px;
    }
    .room-selected {
        border: 2px solid #8b3a22;
        background: #fffaf6;
    }
    .room-title {
        font-size: 20px;
        font-weight: 700;
        color: #2b2118;
    }
    .tag {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 999px;
        background: #f7efe8;
        color: #6f4e37;
        font-size: 12px;
        margin-right: 6px;
        margin-top: 6px;
    }
    .price {
        font-size: 24px;
        font-weight: 800;
        color: #8b3a22;
    }
    .ota-topbar {
        background: linear-gradient(90deg, #1769ff, #00a4ff);
        color: white;
        padding: 18px 22px;
        border-radius: 0 0 22px 22px;
        margin-bottom: 18px;
    }
    .ota-card {
        background: white;
        border-radius: 16px;
        padding: 16px;
        border: 1px solid #e8edf5;
        box-shadow: 0 6px 18px rgba(0, 74, 173, 0.07);
        margin-bottom: 14px;
    }
    .ota-badge {
        display: inline-block;
        background: #fff4e6;
        color: #d46b08;
        padding: 3px 7px;
        border-radius: 6px;
        font-size: 12px;
        margin-right: 5px;
        margin-top: 4px;
    }
    .ota-score {
        background: #1769ff;
        color: white;
        padding: 4px 8px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 700;
    }
    .nudge-box {
        border: 1.5px solid #d8b88a;
        background: #fffaf2;
        border-radius: 16px;
        padding: 18px;
        margin: 16px 0;
        box-shadow: 0 5px 18px rgba(169, 119, 56, 0.10);
    }
    .nudge-title {
        font-size: 18px;
        font-weight: 800;
        color: #6f4518;
        margin-bottom: 8px;
    }
    .small-muted {
        color: #82756a;
        font-size: 13px;
    }
    .step-pill {
        display: inline-block;
        padding: 6px 12px;
        background: #f1ece6;
        border-radius: 999px;
        color: #4b3b2d;
        font-size: 13px;
        margin-right: 6px;
        margin-bottom: 8px;
    }
    .step-active {
        background: #3d2e24;
        color: white;
    }
    .summary-box {
        background: #fbfaf8;
        border: 1px solid #e7e0d7;
        border-radius: 16px;
        padding: 18px;
        position: sticky;
        top: 80px;
    }
    .cart-line {
        display:flex;
        justify-content:space-between;
        border-bottom:1px dashed #ddd4cc;
        padding:8px 0;
        font-size:14px;
    }
    .success-tag {
        display:inline-block;
        background:#e9f8ef;
        color:#137333;
        border:1px solid #bde5c8;
        padding:5px 9px;
        border-radius:999px;
        font-size:13px;
        font-weight:700;
    }
    .warning-tag {
        display:inline-block;
        background:#fff4e6;
        color:#b85c00;
        border:1px solid #ffd59e;
        padding:5px 9px;
        border-radius:999px;
        font-size:13px;
        font-weight:700;
    }
    .bottom-bar {
        background:#ffffff;
        border:1px solid #eee6df;
        border-radius:18px;
        padding:16px;
        box-shadow:0 -4px 22px rgba(0,0,0,0.06);
        margin-top:18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# 2. 初始化状态
# =====================================================
def init_state():
    defaults = {
        "participant_id": str(uuid.uuid4())[:8],
        "stage": 0,
        "events": [],
        "nudge_seen": 0,
        "joined_campaign": False,
        "campaign_choice_made": False,
        "donation_amount": 0.0,
        "campaign_product_name": "",
        "room_selected": "",
        "room_price": 0,
        "hotel_selected": "星澜国际酒店",
        "checkin": date.today() + timedelta(days=7),
        "checkout": date.today() + timedelta(days=8),
        "guest_name": "张先生",
        "guest_phone": "138****8888",
        "searched": False,
        "paid": False,
        # V3.2 修复购物车显示问题：公益加购使用独立、稳定的购物车字段
        "cart_campaign_added": False,
        "cart_campaign_name": "",
        "cart_campaign_price": 0.0,
        # V3.2 修复按钮点击不生效问题：避免每次刷新都改变按钮key
        "nudge_exposed_keys": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

STAGES = ["搜索首页", "酒店详情", "房型选择", "订单确认", "支付页面", "完成问卷"]

DEFAULT_STAGE_MAP = {
    "低频：1次": ["订单确认"],
    "适度：2次": ["酒店详情", "订单确认"],
    "高频：4次": ["搜索首页", "酒店详情", "房型选择", "订单确认"],
}

# =====================================================
# 3. 行为记录与流程控制
# =====================================================
def log_event(event_type, detail=""):
    st.session_state.events.append({
        "participant_id": st.session_state.participant_id,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "interface_mode": st.session_state.get("interface_mode", ""),
        "nudge_frequency": st.session_state.get("nudge_frequency", ""),
        "product_cause_fit": st.session_state.get("product_cause_fit", ""),
        "altruistic_motivation": st.session_state.get("altruistic_motivation", ""),
        "stage": STAGES[st.session_state.stage],
        "event_type": event_type,
        "detail": detail,
    })


def go_stage(idx, reason=""):
    old = STAGES[st.session_state.stage]
    st.session_state.stage = max(0, min(idx, len(STAGES) - 1))
    new = STAGES[st.session_state.stage]
    log_event("navigate", f"{old} -> {new}; {reason}")
    st.rerun()


def next_stage(reason=""):
    go_stage(st.session_state.stage + 1, reason)


def prev_stage(reason=""):
    go_stage(st.session_state.stage - 1, reason)


def reset_experiment():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()
    st.rerun()

# =====================================================
# 4. 研究者控制台
# =====================================================
st.sidebar.title("🧪 研究者控制台")
st.sidebar.caption("V3：页面内真实按钮推进流程，左侧只用于研究者设置实验条件。")

st.session_state.interface_mode = st.sidebar.radio(
    "界面类型",
    ["星级酒店官网模式", "中国OTA App模式"],
)

st.session_state.nudge_frequency = st.sidebar.radio(
    "数字助推频率",
    ["低频：1次", "适度：2次", "高频：4次"],
    index=1,
)

st.session_state.product_cause_fit = st.sidebar.radio(
    "产品—公益匹配度",
    ["高匹配：动物玩偶 + 流浪动物保护", "低匹配：城市明信片 + 流浪动物保护"],
)

st.session_state.altruistic_motivation = st.sidebar.radio(
    "企业公益动机呈现",
    ["高公益动机：长期合作，全部收益捐出", "低公益动机：部分捐出，同时提升品牌形象"],
)

st.sidebar.markdown("---")
st.sidebar.subheader("自定义公益提示出现节点")
use_default = st.sidebar.checkbox("使用默认频率节点", value=True)

if use_default:
    nudge_stages = DEFAULT_STAGE_MAP[st.session_state.nudge_frequency]
else:
    nudge_stages = st.sidebar.multiselect(
        "选择在哪些页面出现公益提示",
        STAGES[:-1],
        default=["酒店详情", "订单确认"],
    )

st.sidebar.markdown("---")
st.sidebar.write(f"被试ID：`{st.session_state.participant_id}`")
st.sidebar.write(f"当前页面：**{STAGES[st.session_state.stage]}**")
st.sidebar.write(f"已选择房型：**{st.session_state.room_selected or '未选择'}**")
st.sidebar.write(f"公益加购：**{'已加入' if st.session_state.joined_campaign else '未加入'}**")
if st.sidebar.button("重置实验"):
    reset_experiment()

# =====================================================
# 5. 通用组件
# =====================================================
def show_steps():
    html = ""
    for idx, s in enumerate(STAGES):
        cls = "step-pill step-active" if idx == st.session_state.stage else "step-pill"
        html += f"<span class='{cls}'>{idx+1}. {s}</span>"
    st.markdown(html, unsafe_allow_html=True)


def get_product_text():
    if "高匹配" in st.session_state.product_cause_fit:
        return "公益动物玩偶", "这款动物玩偶与流浪动物保护项目高度相关，购买后将帮助救助更多流浪动物。"
    return "城市纪念明信片", "这款城市纪念明信片将参与公益活动，部分收益用于流浪动物保护。"


def get_motivation_text():
    if "高公益动机" in st.session_state.altruistic_motivation:
        return "本酒店已长期支持流浪动物救助项目。本次活动所得收益将全部捐赠给合作救助机构，酒店不从中获得商业利润。"
    return "本酒店将把部分收益捐赠给流浪动物救助机构。本活动也有助于提升酒店公益形象，并吸引更多宾客了解酒店品牌。"


def add_campaign_to_order():
    """把公益产品真正加入购物车。V3.1修复：使用更稳定的cart_campaign_*字段，避免页面跳转后状态丢失。"""
    product_name, _ = get_product_text()
    st.session_state.joined_campaign = True
    st.session_state.campaign_choice_made = True
    st.session_state.donation_amount = 9.9
    st.session_state.campaign_product_name = product_name

    # 更稳定的购物车字段：最终结账单优先读取这里
    st.session_state.cart_campaign_added = True
    st.session_state.cart_campaign_name = product_name
    st.session_state.cart_campaign_price = 9.9

    log_event("join_campaign", f"加入公益加购：{product_name} ¥9.9")
    st.toast("已加入公益加购，订单金额已更新。", icon="✅")


def remove_campaign_from_order():
    product_name = st.session_state.get("campaign_product_name") or st.session_state.get("cart_campaign_name") or get_product_text()[0]
    st.session_state.joined_campaign = False
    st.session_state.campaign_choice_made = True
    st.session_state.donation_amount = 0.0
    st.session_state.campaign_product_name = ""

    st.session_state.cart_campaign_added = False
    st.session_state.cart_campaign_name = ""
    st.session_state.cart_campaign_price = 0.0

    log_event("remove_campaign", f"取消公益加购：{product_name}")
    st.toast("已取消公益加购，订单金额已更新。", icon="↩️")


def skip_campaign_order():
    """明确选择暂不参与，也要写入状态，避免后续页面误判。"""
    st.session_state.joined_campaign = False
    st.session_state.campaign_choice_made = True
    st.session_state.donation_amount = 0.0
    st.session_state.campaign_product_name = ""
    st.session_state.cart_campaign_added = False
    st.session_state.cart_campaign_name = ""
    st.session_state.cart_campaign_price = 0.0
    log_event("skip_campaign", "点击暂不参与")
    st.toast("已选择暂不参与公益加购。", icon="ℹ️")


def show_campaign_status():
    campaign_added = st.session_state.get("cart_campaign_added", False) or st.session_state.get("joined_campaign", False)
    campaign_name = st.session_state.get("cart_campaign_name") or st.session_state.get("campaign_product_name") or get_product_text()[0]
    campaign_price = st.session_state.get("cart_campaign_price", 9.9)

    if campaign_added:
        st.markdown(
            f"<span class='success-tag'>已加入购物车：{campaign_name} ¥{campaign_price}</span>",
            unsafe_allow_html=True,
        )
    elif st.session_state.campaign_choice_made:
        st.markdown("<span class='warning-tag'>已选择暂不参与公益加购</span>", unsafe_allow_html=True)


def show_nudge(stage_name):
    """
    公益提示模块 V3.3。
    这次采用 Streamlit 官方更稳定的 on_click 回调写法。
    原因：if st.button(...): 再 st.rerun() 在复杂页面里有时会造成状态没及时进入购物车。
    """
    product_name, product_desc = get_product_text()
    motivation_text = get_motivation_text()

    exposure_key = f"{stage_name}_{st.session_state.nudge_frequency}_{st.session_state.product_cause_fit}_{st.session_state.altruistic_motivation}"
    if exposure_key not in st.session_state.nudge_exposed_keys:
        st.session_state.nudge_seen += 1
        st.session_state.nudge_exposed_keys.append(exposure_key)
        log_event("nudge_exposed", f"第{st.session_state.nudge_seen}次看到公益提示：{stage_name}")

    st.markdown(
        f"""
        <div class="nudge-box">
            <div class="nudge-title">🐾 公益住宿计划 · {product_name}</div>
            <div>{product_desc}</div>
            <div class="small-muted" style="margin-top:8px;">{motivation_text}</div>
            <div class="small-muted" style="margin-top:8px;">您可自愿加入公益加购，支持该项目。该选择不会影响您的房间预订。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    campaign_added = st.session_state.get("cart_campaign_added", False)

    if campaign_added:
        show_campaign_status()
        st.button(
            "取消公益加购",
            key=f"remove_campaign_btn_{stage_name}",
            on_click=remove_campaign_from_order,
        )
    else:
        c1, c2, c3 = st.columns([1.2, 1, 3])
        with c1:
            st.button(
                "加入公益加购 ¥9.9",
                key=f"join_campaign_btn_{stage_name}",
                on_click=add_campaign_to_order,
                type="primary",
            )
        with c2:
            st.button(
                "暂不参与",
                key=f"skip_campaign_btn_{stage_name}",
                on_click=skip_campaign_order,
            )

def maybe_show_nudge():
    current_stage = STAGES[st.session_state.stage]
    if current_stage in nudge_stages:
        show_nudge(current_stage)


def nights_count():
    try:
        days = (st.session_state.checkout - st.session_state.checkin).days
        return max(days, 1)
    except Exception:
        return 1


def total_price():
    campaign_price = st.session_state.get("cart_campaign_price", 0.0) if st.session_state.get("cart_campaign_added", False) else 0.0
    return st.session_state.room_price * nights_count() + campaign_price


def order_summary(show_actions=True):
    nights = nights_count()
    st.markdown("<div class='summary-box'>", unsafe_allow_html=True)
    st.markdown("### 订单摘要")
    st.markdown(f"<div class='cart-line'><span>酒店</span><b>{st.session_state.hotel_selected}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>房型</span><b>{st.session_state.room_selected or '未选择'}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>入住</span><b>{st.session_state.checkin}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>离店</span><b>{st.session_state.checkout}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>晚数</span><b>{nights}晚</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>房费</span><b>¥{st.session_state.room_price * nights}</b></div>", unsafe_allow_html=True)

    campaign_added = st.session_state.get("cart_campaign_added", False) or st.session_state.get("joined_campaign", False)
    campaign_name = st.session_state.get("cart_campaign_name") or st.session_state.get("campaign_product_name") or get_product_text()[0]
    campaign_price = st.session_state.get("cart_campaign_price", 9.9) if campaign_added else 0.0

    if campaign_added:
        st.markdown(
            f"<div class='cart-line'><span>{campaign_name}</span><b>¥{campaign_price}</b></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<span class='success-tag'>公益加购已加入最终结账单</span>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='cart-line'><span>公益加购</span><b>未加入</b></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='price' style='margin-top:14px;'>合计 ¥{total_price():.1f}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if show_actions and (st.session_state.get("cart_campaign_added", False) or st.session_state.get("joined_campaign", False)):
        if st.button("从订单中移除公益加购", key="summary_remove_campaign"):
            remove_campaign_from_order()
            st.rerun()


def bottom_navigation(back_label="返回", next_label="继续", next_disabled=False, next_reason=""):
    st.markdown("<div class='bottom-bar'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.session_state.stage > 0:
            if st.button(f"← {back_label}", use_container_width=True, key=f"back_{st.session_state.stage}"):
                prev_stage("页面底部返回按钮")
    with c3:
        if st.session_state.stage < len(STAGES) - 1:
            if st.button(f"{next_label} →", disabled=next_disabled, use_container_width=True, key=f"next_{st.session_state.stage}"):
                next_stage(next_reason or "页面底部继续按钮")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# 6. 星级酒店官网模式
# =====================================================
def hotel_header():
    st.markdown(
        """
        <div class="main-header">
            <div>
                <div class="brand-title">LUXE ACADEMIA HOTEL</div>
                <div class="brand-subtitle">星澜国际酒店 · 直接预订 · 会员礼遇 · 会议活动</div>
            </div>
            <div>
                <span class="nav-item">查找与预订</span>
                <span class="nav-item">优惠活动</span>
                <span class="nav-item">会议与活动</span>
                <span class="nav-item">登录 / 加入会员</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hotel_search_panel():
    st.markdown("<div class='search-box'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([2.2, 1.2, 1.2, 1.4, 1.2])
    with c1:
        st.text_input("目的地", value="厦门 / Xiamen", key="hotel_dest")
    with c2:
        st.session_state.checkin = st.date_input("入住日期", value=st.session_state.checkin, key="hotel_checkin")
    with c3:
        st.session_state.checkout = st.date_input("离店日期", value=st.session_state.checkout, key="hotel_checkout")
    with c4:
        st.selectbox("客房及宾客", ["1间客房，2位宾客", "1间客房，1位宾客", "2间客房，4位宾客"], key="hotel_guests")
    with c5:
        st.selectbox("特别房价", ["标准房价", "会员房价", "企业协议价", "使用积分"], key="hotel_rate")
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        if st.button("查找酒店", type="primary", use_container_width=True):
            st.session_state.searched = True
            log_event("search_hotel", "酒店官网点击查找酒店")
            next_stage("查找酒店后进入酒店详情")
    with c2:
        if st.button("查看可订房型", use_container_width=True):
            st.session_state.searched = True
            log_event("search_rooms", "酒店官网点击查看可订房型")
            go_stage(2, "直接查看房型")


def render_hotel_website(stage):
    hotel_header()
    show_steps()

    if stage == 0:
        st.markdown(
            """
            <div class="hero">
                <h1>于城市与校园之间，开启从容旅居</h1>
                <p>探索兼具学术气质与高端服务体验的城市酒店。直接预订，尊享灵活房价、免费Wi-Fi与专属礼遇。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        hotel_search_panel()
        maybe_show_nudge()
        st.markdown("### 精选礼遇")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<div class='lux-card'><b>会员房价</b><br><span class='small-muted'>加入会员，享受专属预订优惠。</span></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='lux-card'><b>免费 Wi-Fi</b><br><span class='small-muted'>入住期间畅享高速无线网络。</span></div>", unsafe_allow_html=True)
        with c3:
            st.markdown("<div class='lux-card'><b>会议与活动</b><br><span class='small-muted'>专业会议空间与高标准服务支持。</span></div>", unsafe_allow_html=True)

    elif stage == 1:
        left, right = st.columns([2, 1])
        with left:
            st.markdown("## 星澜国际酒店 · 厦门")
            st.caption("Siming District, Xiamen · 距主要景区约15分钟车程")
            st.image("https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=1400", use_container_width=True)
            st.markdown("<span class='tag'>高端酒店</span><span class='tag'>会议设施</span><span class='tag'>免费Wi-Fi</span><span class='tag'>灵活取消</span>", unsafe_allow_html=True)
            st.write("酒店融合现代设计与在地文化，适合商务出行、学术会议与休闲度假。")
            maybe_show_nudge()
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("查看房型与价格", type="primary", use_container_width=True):
                    log_event("view_rooms", "酒店详情页点击查看房型与价格")
                    next_stage("查看房型与价格")
            with c2:
                if st.button("返回重新搜索", use_container_width=True):
                    prev_stage("返回搜索首页")
        with right:
            st.markdown("<div class='lux-card'><h3>宾客评分 4.8/5</h3><p class='small-muted'>环境、服务与位置获得高度评价</p><hr><b>热门设施</b><br>健身中心 · 餐厅 · 会议室 · 礼宾服务</div>", unsafe_allow_html=True)

    elif stage == 2:
        st.markdown("## 选择房型")
        rooms = [
            ("豪华大床房", 688, "35㎡ · 1张大床 · 城市景观", ["含双早", "免费取消", "会员积分"]),
            ("高级双床房", 728, "38㎡ · 2张单人床 · 适合双人出行", ["含双早", "适合差旅", "免费Wi-Fi"]),
            ("行政湖景房", 988, "45㎡ · 湖景 · 行政礼遇", ["行政礼遇", "延迟退房", "景观房"]),
        ]
        for name, price, desc, tags in rooms:
            selected_class = " room-selected" if st.session_state.room_selected == name else ""
            c1, c2 = st.columns([3, 1])
            with c1:
                tag_html = "".join([f"<span class='tag'>{t}</span>" for t in tags])
                selected_text = "<span class='success-tag'>当前已选</span>" if st.session_state.room_selected == name else ""
                st.markdown(f"<div class='room-card{selected_class}'><div class='room-title'>{name} {selected_text}</div><div class='small-muted'>{desc}</div>{tag_html}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='price'>¥{price}</div>", unsafe_allow_html=True)
                if st.button(f"选择并预订", key=f"hotel_room_{name}", type="primary" if st.session_state.room_selected == name else "secondary", use_container_width=True):
                    st.session_state.room_selected = name
                    st.session_state.room_price = price
                    log_event("select_room", f"选择{name} ¥{price}")
                    next_stage(f"选择房型：{name}")
        maybe_show_nudge()
        bottom_navigation("返回酒店详情", "继续确认订单", next_disabled=(not st.session_state.room_selected), next_reason="房型页继续确认订单")

    elif stage == 3:
        left, right = st.columns([2, 1])
        with left:
            st.markdown("## 确认订单")
            st.markdown("<div class='lux-card'><b>入住人信息</b></div>", unsafe_allow_html=True)
            st.session_state.guest_name = st.text_input("入住人姓名", value=st.session_state.guest_name)
            st.session_state.guest_phone = st.text_input("手机号", value=st.session_state.guest_phone)
            st.markdown("<div class='lux-card'><b>预订政策</b><br>入住当天18:00前可免费取消。到店需出示有效身份证件。</div>", unsafe_allow_html=True)
            maybe_show_nudge()
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("返回修改房型", use_container_width=True):
                    prev_stage("订单确认页返回修改房型")
            with c2:
                if st.button("确认订单并去支付", type="primary", use_container_width=True, disabled=(not st.session_state.room_selected)):
                    log_event("confirm_order", f"确认订单，总金额 ¥{total_price():.1f}")
                    next_stage("确认订单并去支付")
        with right:
            order_summary()

    elif stage == 4:
        left, right = st.columns([2, 1])
        with left:
            st.markdown("## 支付页面")
            st.markdown("<div class='lux-card'><b>选择支付方式</b><br>微信支付 · 支付宝 · 银行卡 · 企业转账</div>", unsafe_allow_html=True)
            maybe_show_nudge()
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("返回修改订单", use_container_width=True):
                    prev_stage("支付页返回修改订单")
            with c2:
                if st.button(f"确认支付 ¥{total_price():.1f}", type="primary", use_container_width=True):
                    st.session_state.paid = True
                    log_event("pay_order", f"模拟支付成功，总金额 ¥{total_price():.1f}")
                    next_stage("支付完成进入问卷")
        with right:
            order_summary()

    elif stage == 5:
        render_survey_and_export()

# =====================================================
# 7. OTA模式
# =====================================================
def ota_header():
    st.markdown(
        """
        <div class="ota-topbar">
            <h2 style="margin:0;">旅程优选</h2>
            <div style="font-size:13px; opacity:0.9;">模拟中国OTA App酒店预订流程 · 搜索 · 比价 · 下单 · 支付</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ota_app(stage):
    ota_header()
    show_steps()

    if stage == 0:
        st.markdown("### 搜索酒店")
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1:
            st.text_input("目的地/酒店/关键词", value="厦门大学附近", key="ota_kw")
        with c2:
            st.session_state.checkin = st.date_input("入住", value=st.session_state.checkin, key="ota_in")
        with c3:
            st.session_state.checkout = st.date_input("离店", value=st.session_state.checkout, key="ota_out")
        with c4:
            st.selectbox("人数", ["2成人", "1成人", "2成人1儿童"], key="ota_people")
        if st.button("搜索酒店", type="primary", use_container_width=True):
            st.session_state.searched = True
            log_event("ota_search", "OTA点击搜索酒店")
            st.toast("已为您找到附近酒店。", icon="🔎")
        maybe_show_nudge()
        st.markdown("### 推荐酒店")
        hotels = [
            ("星澜国际酒店", "4.8", "近厦门大学 · 高端型 · 会议设施", 688, ["特牌推荐", "含早", "可取消"]),
            ("海岸花园酒店", "4.6", "近沙坡尾 · 亲子友好 · 性价比高", 528, ["今日低价", "近景区", "闪住"]),
            ("城景悦居酒店", "4.5", "近商圈 · 商务出行 · 交通便利", 468, ["限时优惠", "免费取消", "高分好评"]),
        ]
        for h, score, desc, price, badges in hotels:
            badge_html = "".join([f"<span class='ota-badge'>{b}</span>" for b in badges])
            c1, c2 = st.columns([4, 1])
            with c1:
                selected_text = " <span class='success-tag'>当前浏览</span>" if st.session_state.hotel_selected == h else ""
                st.markdown(
                    f"""
                    <div class="ota-card">
                        <h3 style="margin-bottom:4px;">{h}{selected_text}</h3>
                        <div class="small-muted">{desc}</div>
                        <div>{badge_html}</div>
                        <div style="margin-top:8px;"><span class="ota-score">{score}分</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(f"<div class='price'>¥{price}</div><span class='small-muted'>起</span>", unsafe_allow_html=True)
                if st.button("查看详情", key=f"ota_view_{h}", type="primary" if h == "星澜国际酒店" else "secondary", use_container_width=True):
                    st.session_state.hotel_selected = h
                    log_event("ota_select_hotel", f"选择酒店：{h}")
                    next_stage(f"查看酒店详情：{h}")

    elif stage == 1:
        st.markdown(f"## {st.session_state.hotel_selected}")
        st.image("https://images.unsplash.com/photo-1564501049412-61c2a3083791?q=80&w=1400", use_container_width=True)
        st.markdown("<span class='ota-score'>4.8分</span> <span class='ota-badge'>高端型</span><span class='ota-badge'>近厦门大学</span><span class='ota-badge'>会议设施</span>", unsafe_allow_html=True)
        st.markdown("<div class='ota-card'><b>住客点评</b><br>位置便利，服务细致，适合商务会议与家庭旅行。</div>", unsafe_allow_html=True)
        maybe_show_nudge()
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("返回酒店列表", use_container_width=True):
                prev_stage("OTA详情页返回列表")
        with c2:
            if st.button("选择房型", type="primary", use_container_width=True):
                log_event("ota_go_rooms", "OTA详情页点击选择房型")
                next_stage("进入房型选择")

    elif stage == 2:
        st.markdown("## 房型列表")
        rooms = [
            ("豪华大床房", 688, "含双早 | 免费取消 | 到店付/在线付"),
            ("高级双床房", 728, "双床 | 适合朋友出行 | 免费Wi-Fi"),
            ("行政湖景房", 988, "湖景 | 行政礼遇 | 延迟退房"),
        ]
        for name, price, desc in rooms:
            selected_class = " room-selected" if st.session_state.room_selected == name else ""
            c1, c2 = st.columns([3, 1])
            with c1:
                selected_text = "<span class='success-tag'>当前已选</span>" if st.session_state.room_selected == name else ""
                st.markdown(f"<div class='ota-card{selected_class}'><h3>{name} {selected_text}</h3><div class='small-muted'>{desc}</div><span class='ota-badge'>仅剩3间</span><span class='ota-badge'>订后可取消</span></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='price'>¥{price}</div>", unsafe_allow_html=True)
                if st.button("预订", key=f"ota_room_{name}", type="primary" if st.session_state.room_selected == name else "secondary", use_container_width=True):
                    st.session_state.room_selected = name
                    st.session_state.room_price = price
                    log_event("select_room", f"OTA选择{name} ¥{price}")
                    next_stage(f"OTA选择房型：{name}")
        maybe_show_nudge()
        bottom_navigation("返回酒店详情", "继续填写订单", next_disabled=(not st.session_state.room_selected), next_reason="OTA房型页继续")

    elif stage == 3:
        left, right = st.columns([2, 1])
        with left:
            st.markdown("## 填写订单")
            st.markdown("<div class='ota-card'><b>入住人信息</b></div>", unsafe_allow_html=True)
            st.session_state.guest_name = st.text_input("入住人姓名", value=st.session_state.guest_name, key="ota_guest_name")
            st.session_state.guest_phone = st.text_input("手机号", value=st.session_state.guest_phone, key="ota_guest_phone")
            st.markdown("<div class='ota-card'><b>优惠信息</b><br><span class='ota-badge'>平台立减 ¥20</span><span class='ota-badge'>会员返积分</span></div>", unsafe_allow_html=True)
            maybe_show_nudge()
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("返回修改房型", use_container_width=True):
                    prev_stage("OTA订单页返回房型")
            with c2:
                if st.button("提交订单", type="primary", use_container_width=True, disabled=(not st.session_state.room_selected)):
                    log_event("ota_submit_order", f"OTA提交订单，总金额 ¥{total_price():.1f}")
                    next_stage("提交订单进入支付")
        with right:
            order_summary()

    elif stage == 4:
        left, right = st.columns([2, 1])
        with left:
            st.markdown("## 确认支付")
            st.markdown("<div class='ota-card'><b>支付方式</b><br>支付宝 · 微信支付 · 银行卡</div>", unsafe_allow_html=True)
            maybe_show_nudge()
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("返回修改订单", use_container_width=True):
                    prev_stage("OTA支付页返回订单")
            with c2:
                if st.button(f"确认支付 ¥{total_price():.1f}", type="primary", use_container_width=True):
                    st.session_state.paid = True
                    log_event("ota_pay_order", f"OTA模拟支付成功，总金额 ¥{total_price():.1f}")
                    next_stage("支付完成进入问卷")
        with right:
            order_summary()

    elif stage == 5:
        render_survey_and_export()

# =====================================================
# 8. 问卷与导出
# =====================================================
def likert(label, key):
    return st.slider(label, 1, 7, 4, key=key)


def render_survey_and_export():
    st.success("预订流程已完成。请填写以下实验问卷。")
    if st.session_state.paid:
        st.markdown("<span class='success-tag'>模拟支付成功</span>", unsafe_allow_html=True)
    show_campaign_status()

    st.subheader("A. 心理抗拒 Psychological Reactance")
    r1 = likert("我觉得这个公益提示有点打扰我的选择。", "r1")
    r2 = likert("我觉得酒店/平台在试图影响我的决定。", "r2")
    r3 = likert("我觉得这些提示有一点强迫感。", "r3")
    r4 = likert("我对反复出现的公益提示感到反感。", "r4")

    st.subheader("B. 参与意愿 Participation Intention")
    i1 = likert("我愿意参与该公益营销活动。", "i1")
    i2 = likert("我愿意为该公益项目提供支持。", "i2")
    i3 = likert("如果真实入住，我可能会选择公益加购。", "i3")

    st.subheader("C. 操纵检验 Manipulation Check")
    f1 = likert("我觉得公益提示出现得很频繁。", "f1")
    fit1 = likert("我觉得产品和公益项目很匹配。", "fit1")
    alt1 = likert("我觉得酒店是真心想帮助公益对象。", "alt1")

    result = {
        "participant_id": st.session_state.participant_id,
        "interface_mode": st.session_state.interface_mode,
        "nudge_frequency": st.session_state.nudge_frequency,
        "product_cause_fit": st.session_state.product_cause_fit,
        "altruistic_motivation": st.session_state.altruistic_motivation,
        "hotel_selected": st.session_state.hotel_selected,
        "room_selected": st.session_state.room_selected,
        "room_price": st.session_state.room_price,
        "nights": nights_count(),
        "joined_campaign": "是" if st.session_state.joined_campaign else "否",
        "campaign_product_name": st.session_state.campaign_product_name,
        "donation_amount": st.session_state.donation_amount,
        "total_price": total_price(),
        "nudge_seen": st.session_state.nudge_seen,
        "paid": "是" if st.session_state.paid else "否",
        "reactance_mean": round((r1 + r2 + r3 + r4) / 4, 2),
        "intention_mean": round((i1 + i2 + i3) / 3, 2),
        "perceived_frequency": f1,
        "perceived_fit": fit1,
        "perceived_altruism": alt1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    st.subheader("实验结果预览")
    st.dataframe(pd.DataFrame([result]), use_container_width=True)

    events_df = pd.DataFrame(st.session_state.events)
    result_df = pd.DataFrame([result])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "下载本名被试结果CSV",
            result_df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"participant_{st.session_state.participant_id}_result.csv",
            mime="text/csv",
        )
    with c2:
        st.download_button(
            "下载行为日志CSV",
            events_df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"participant_{st.session_state.participant_id}_events.csv",
            mime="text/csv",
        )
    with c3:
        if st.button("重新开始一个新被试"):
            reset_experiment()

# =====================================================
# 9. 主程序
# =====================================================
st.markdown("## 酒店预订实验模拟页面 V3")
st.caption("本版本已改为页面内真实交互：搜索、查看详情、选择房型、公益加购、确认订单、支付、问卷。")

if st.session_state.interface_mode == "星级酒店官网模式":
    render_hotel_website(st.session_state.stage)
else:
    render_ota_app(st.session_state.stage)
