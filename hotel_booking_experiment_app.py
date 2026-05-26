import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import uuid
from pathlib import Path

# =========================================================
# 酒店预订实验系统 V4.2
# 主要功能：
# 1. 分为“受试者页面”和“后台管理页面”两层。
# 2. 受试者看不到控制台、条件设置和数据下载。
# 3. 后台页面通过 URL 参数 ?admin=1 进入。
# 4. 酒店官网界面加入酒店主图、图集、房型图片。
# 5. OTA 界面改为更接近真实 OTA 的酒店列表、详情、房型卡片。
# 6. 公益计划按高匹配/低匹配展示：动物公仔 / 明信片。
# 7. 最后一页问卷顺序：操纵检验 → 心理机制 → 调节变量 → 人口信息。
# =========================================================

st.set_page_config(
    page_title="星澜酒店预订",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = Path("experiment_data.csv")
EVENT_PATH = Path("experiment_events.csv")

HOTEL_CN = "星澜酒店"
HOTEL_EN = "Starland Hotel"

# 公益产品图片：请在项目目录中新建 assets 文件夹，并放入这两个图片文件。
# assets/campaign_toy.png：动物公仔图片
# assets/campaign_postcard.png：明信片图片
TOY_IMAGE_PATH = Path("assets/campaign_toy.png")
POSTCARD_IMAGE_PATH = Path("assets/campaign_postcard.png")

STAGES = ["浏览首页", "酒店详情", "房型选择", "订单确认", "支付页面", "完成问卷"]

DEFAULT_STAGE_MAP = {
    "低频：仅支付前出现1次": ["订单确认"],
    "中频：浏览与订单阶段出现2次": ["酒店详情", "订单确认"],
    "高频：多阶段重复出现4次": ["浏览首页", "酒店详情", "房型选择", "订单确认"],
}

# 图片使用公开图库链接。正式实验时建议换成你自己准备的酒店/房型图片，避免外部链接加载不稳定。
HOTEL_IMAGES = [
    "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1600&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1564501049412-61c2a3083791?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1522798514-97ceb8c4f1c8?q=80&w=1200&auto=format&fit=crop",
]

ROOMS = [
    {
        "name": "舒适大床房",
        "price": 688,
        "desc": "约28㎡，一张大床，安静楼层，适合商务出行与短途旅行。",
        "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?q=80&w=1200&auto=format&fit=crop",
        "tags": ["大床", "免费Wi-Fi", "城市出行", "可开发票"],
    },
    {
        "name": "高级大床房",
        "price": 788,
        "desc": "约32㎡，城市景观，办公桌与休闲沙发，配备高速无线网络。",
        "img": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?q=80&w=1200&auto=format&fit=crop",
        "tags": ["城市景观", "办公桌", "高速网络", "早餐可选"],
    },
    {
        "name": "行政大床房",
        "price": 988,
        "desc": "约38㎡，高楼层视野，迷你吧与欢迎水果，适合高品质住宿需求。",
        "img": "https://images.unsplash.com/photo-1590490360182-c33d57733427?q=80&w=1200&auto=format&fit=crop",
        "tags": ["高楼层", "迷你吧", "欢迎水果", "延迟退房"],
    },
]

OTA_HOTELS = [
    {
        "name": HOTEL_CN,
        "en": HOTEL_EN,
        "score": "4.8",
        "comment": "棒",
        "price": 688,
        "desc": "近商圈 · 舒适型酒店 · 商务休闲皆宜",
        "distance": "距市中心约1.2公里",
        "img": HOTEL_IMAGES[0],
        "badges": ["近地铁", "免费Wi-Fi", "好评高", "可取消"],
        "is_target": True,
    },
    {
        "name": "云栖酒店",
        "en": "Cloudstay Hotel",
        "score": "4.7",
        "comment": "很好",
        "price": 628,
        "desc": "近景点 · 设计感强 · 适合情侣出游",
        "distance": "距市中心约1.8公里",
        "img": HOTEL_IMAGES[1],
        "badges": ["设计感", "安静", "位置好"],
        "is_target": False,
    },
    {
        "name": "泊悦酒店",
        "en": "Harbor Hotel",
        "score": "4.6",
        "comment": "很好",
        "price": 598,
        "desc": "交通便利 · 适合差旅 · 性价比高",
        "distance": "距市中心约2.4公里",
        "img": HOTEL_IMAGES[2],
        "badges": ["性价比", "商务", "可取消"],
        "is_target": False,
    },
]

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1180px;}
    .main-title {font-size: 30px; font-weight: 800; color: #232323; line-height:1.35; padding-top:10px; margin:10px 0 8px 0; overflow:visible;}
    .sub-title {font-size: 15px; color: #6b7280; line-height:1.6; margin-bottom: 18px;}
    .topbar {display:flex; align-items:center; justify-content:space-between; min-height:76px; padding:20px 22px 18px 22px; border:1px solid #ece7df; border-radius:18px; background:#fffaf4; margin:10px 0 18px 0; overflow:visible; box-sizing:border-box;}
    .brand-cn {font-size:24px; font-weight:800; color:#442c1d; line-height:1.35; padding-top:2px; overflow:visible;}
    .brand-en {font-size:13px; color:#7a6a5c; margin-top:4px; line-height:1.35;}
    .pill {display:inline-block; padding:5px 10px; border-radius:999px; background:#f3eee7; color:#6d4c35; font-size:12px; margin-right:6px; margin-bottom:6px;}
    .hero {border-radius:24px; background:linear-gradient(135deg,#f7efe4,#ffffff); border:1px solid #ead8c5; padding:32px; margin-bottom:20px;}
    .hero h1 {font-size:36px; margin:0 0 10px 0; color:#3b2b20;}
    .hero p {font-size:16px; color:#5f5147; max-width:760px; line-height:1.8;}
    .search-card {border:1px solid #ead8c5; border-radius:20px; padding:18px; background:#ffffff; box-shadow:0 8px 30px rgba(80,50,20,.06); margin-bottom:20px;}
    .hotel-card {border:1px solid #e8e0d7; border-radius:22px; padding:20px; background:#ffffff; box-shadow:0 8px 28px rgba(0,0,0,.05); margin-bottom:16px;}
    .hotel-name {font-size:25px; font-weight:800; color:#2f241c; margin-bottom:4px;}
    .score {font-size:18px; font-weight:800; color:#9a5b22;}
    .small-muted {font-size:13px; color:#777; line-height:1.7;}
    .room-card {border:1px solid #e5ded4; border-radius:18px; padding:16px; background:#fff; margin-bottom:14px; box-shadow:0 8px 24px rgba(0,0,0,.045);}
    .room-title {font-size:19px; font-weight:750; color:#2d241c;}
    .price {font-size:24px; font-weight:850; color:#8b3f20;}
    .nudge-box {border:1.5px solid #ddb985; background:#fffaf4; border-radius:18px; padding:18px 20px; margin:16px 0;}
    .nudge-title {font-size:20px; font-weight:800; color:#5a3518; margin-bottom:10px;}
    .campaign-img img {border-radius:16px; border:1px solid #ead8c5; object-fit:cover;}
    .success-tag {display:inline-block; background:#e8f7eb; color:#087a37; border:1px solid #bfe8ca; border-radius:999px; padding:7px 12px; font-size:13px; font-weight:700; margin:8px 0;}
    .warning-tag {display:inline-block; background:#fff5df; color:#8a5a00; border:1px solid #f0d28b; border-radius:999px; padding:7px 12px; font-size:13px; font-weight:700; margin:8px 0;}
    .order-box {border:1px solid #e5ded4; border-radius:22px; padding:22px; background:#fff; position:sticky; top:20px; box-shadow:0 8px 26px rgba(0,0,0,.05);}
    .order-box h3 {font-size:24px; margin:0 0 18px 0;}
    .cart-line {display:flex; justify-content:space-between; border-bottom:1px dashed #ddd2c8; padding:10px 0; font-size:15px;}
    .total {font-size:24px; font-weight:850; color:#8b3f20; margin-top:18px;}
    .steps {display:flex; gap:8px; flex-wrap:wrap; margin:16px 0 22px 0;}
    .step-on {background:#6d4c35;color:white;padding:7px 12px;border-radius:999px;font-size:13px;}
    .step-off {background:#f2eee9;color:#6b625c;padding:7px 12px;border-radius:999px;font-size:13px;}
    .admin-box {border:1px solid #d6d3d1; border-radius:16px; padding:16px; background:#fafafa; margin-bottom:16px;}
    .image-note {font-size:12px;color:#8a8178;margin-top:5px;}
    .hotel-gallery img {border-radius:18px; object-fit:cover;}
    .room-photo img {border-radius:16px; object-fit:cover;}
    .ota-shell {max-width:480px; margin:auto; border:1px solid #e5e1dc; border-radius:30px; background:#f7f8fa; padding:14px; box-shadow:0 10px 35px rgba(0,0,0,.10);}
    .ota-inner {background:#fff; border-radius:24px; padding:16px; min-height:720px;}
    .ota-header {display:flex; justify-content:space-between; align-items:center; font-size:22px; font-weight:850; margin-bottom:12px;}
    .ota-search {background:#f2f4f7;border-radius:14px;padding:12px;margin-bottom:12px;color:#555;font-size:14px;}
    .ota-list-card {border:1px solid #e7e1d8; border-radius:18px; padding:12px; background:#fff; margin-bottom:14px; box-shadow:0 6px 18px rgba(0,0,0,.05);}
    .ota-list-title {font-size:17px; font-weight:800; margin-bottom:4px;}
    .ota-tag {display:inline-block; background:#f0f6ff; color:#245d9c; padding:3px 7px; border-radius:999px; font-size:11px; margin-right:4px; margin-bottom:4px;}
    .ota-score {font-weight:850; color:#fff; background:#1d63b7; border-radius:8px; padding:3px 6px; font-size:12px;}
    .ota-price {font-size:20px; font-weight:850; color:#e24a1a; text-align:right;}
    .ota-room-card {border:1px solid #e8e2da; border-radius:16px; background:#fff; padding:12px; margin-bottom:12px; box-shadow:0 5px 16px rgba(0,0,0,.04);}
    </style>
    """,
    unsafe_allow_html=True,
)


def is_admin_page():
    return st.query_params.get("admin", "0") == "1"


def init_state():
    defaults = {
        "participant_id": str(uuid.uuid4())[:8],
        "stage": "浏览首页",
        "interface_mode": "酒店官网界面",
        "nudge_frequency": "中频：浏览与订单阶段出现2次",
        "product_cause_fit": "高匹配：毛绒公仔 × 濒危动物保护",
        "altruistic_motivation": "高利他动机：全部收益捐出",
        "selected_room": "",
        "room_price": 0,
        "check_in": date.today() + timedelta(days=7),
        "check_out": date.today() + timedelta(days=8),
        "guest_count": 1,
        "joined_campaign": False,
        "campaign_choice_made": False,
        "donation_amount": 0.0,
        "campaign_product_name": "",
        "cart_campaign_added": False,
        "cart_campaign_name": "",
        "cart_campaign_price": 0.0,
        "nudge_seen": 0,
        "nudge_exposed_keys": [],
        "paid": False,
        "events": [],
        "survey_submitted": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def log_event(event_type, detail=""):
    event = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "participant_id": st.session_state.participant_id,
        "stage": st.session_state.stage,
        "event_type": event_type,
        "detail": detail,
    }
    st.session_state.events.append(event)


def save_events_to_csv():
    if not st.session_state.events:
        return
    df = pd.DataFrame(st.session_state.events)
    header = not EVENT_PATH.exists()
    df.to_csv(EVENT_PATH, mode="a", index=False, header=header, encoding="utf-8-sig")
    st.session_state.events = []


def save_result_to_csv(result):
    df = pd.DataFrame([result])
    header = not DATA_PATH.exists()
    df.to_csv(DATA_PATH, mode="a", index=False, header=header, encoding="utf-8-sig")


def reset_experiment():
    keep_admin = st.query_params.get("admin", "0")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params["admin"] = keep_admin
    init_state()
    st.rerun()


def go_stage(stage):
    st.session_state.stage = stage
    log_event("go_stage", stage)


def next_stage():
    idx = STAGES.index(st.session_state.stage)
    if idx < len(STAGES) - 1:
        go_stage(STAGES[idx + 1])


def prev_stage():
    idx = STAGES.index(st.session_state.stage)
    if idx > 0:
        go_stage(STAGES[idx - 1])


def get_nudge_stages():
    return DEFAULT_STAGE_MAP.get(st.session_state.nudge_frequency, ["订单确认"])


def get_product_text():
    if st.session_state.product_cause_fit.startswith("高匹配"):
        return (
            "公益动物玩偶",
            "【公益计划】本酒店长期与濒危动物保护基金会合作开展公益活动。您愿意购买这个毛绒公仔来参加此次公益项目吗？活动的全部收益都将捐出用于濒危动物的保护工作。",
        )
    return (
        "公益明信片",
        "【公益计划】本酒店长期与濒危动物保护基金会合作开展公益活动。您愿意购买这款明信片来支持此次公益项目吗？活动的全部收益都将捐出用于濒危动物的保护工作。",
    )


def get_campaign_image_path():
    """根据高/低匹配度返回公益产品图片。图片不存在时返回 None，避免程序报错。"""
    if st.session_state.product_cause_fit.startswith("高匹配"):
        return TOY_IMAGE_PATH if TOY_IMAGE_PATH.exists() else None
    return POSTCARD_IMAGE_PATH if POSTCARD_IMAGE_PATH.exists() else None


def get_motivation_text():
    if st.session_state.altruistic_motivation.startswith("高利他"):
        return "本次活动收益将全额捐赠给合作基金会，酒店不从中获得商业利润。"
    return "本次活动收益将用于公益项目及酒店公益合作项目的运营推广。"


def add_campaign_to_order():
    product_name, _ = get_product_text()
    st.session_state.joined_campaign = True
    st.session_state.campaign_choice_made = True
    st.session_state.donation_amount = 9.9
    st.session_state.campaign_product_name = product_name
    st.session_state.cart_campaign_added = True
    st.session_state.cart_campaign_name = product_name
    st.session_state.cart_campaign_price = 9.9
    log_event("join_campaign", f"加入公益加购：{product_name} ¥9.9")
    st.toast("已加入公益加购，订单金额已更新。", icon="✅")


def remove_campaign_from_order():
    product_name = st.session_state.get("cart_campaign_name") or get_product_text()[0]
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
    if st.session_state.get("cart_campaign_added", False):
        st.markdown(
            f"<span class='success-tag'>已加入购物车：{st.session_state.cart_campaign_name} ¥{st.session_state.cart_campaign_price}</span>",
            unsafe_allow_html=True,
        )
    elif st.session_state.campaign_choice_made:
        st.markdown("<span class='warning-tag'>已选择暂不参与公益加购</span>", unsafe_allow_html=True)


def show_nudge(stage_name):
    product_name, product_desc = get_product_text()
    motivation_text = get_motivation_text()
    product_image = get_campaign_image_path()
    exposure_key = f"{stage_name}_{st.session_state.nudge_frequency}_{st.session_state.product_cause_fit}_{st.session_state.altruistic_motivation}"
    if exposure_key not in st.session_state.nudge_exposed_keys:
        st.session_state.nudge_seen += 1
        st.session_state.nudge_exposed_keys.append(exposure_key)
        log_event("nudge_exposed", f"第{st.session_state.nudge_seen}次看到公益提示：{stage_name}")

    st.markdown("<div class='nudge-box'>", unsafe_allow_html=True)
    img_col, text_col = st.columns([0.9, 3])
    with img_col:
        if product_image:
            st.image(str(product_image), use_container_width=True)
        else:
            st.markdown(
                "<div class='small-muted' style='padding:22px;border:1px dashed #d8c4aa;border-radius:14px;text-align:center;'>公益产品图片</div>",
                unsafe_allow_html=True,
            )
    with text_col:
        st.markdown(
            f"""
            <div class="nudge-title">🐾 {product_name}</div>
            <div style="font-size:16px; line-height:1.8; color:#3f332b;">{product_desc}</div>
            <div class="small-muted" style="margin-top:8px;">{motivation_text}</div>
            <div class="small-muted" style="margin-top:10px; font-weight:700; color:#7a5a38;">可选公益加购，不影响房型选择与酒店预订。</div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("cart_campaign_added", False):
        show_campaign_status()
        st.button(
            "取消公益加购",
            key=f"remove_campaign_btn_{stage_name}",
            on_click=remove_campaign_from_order,
            type="secondary",
        )
    else:
        st.caption("以下为可选公益参与项，与继续查看房型/确认订单按钮不同。")
        c1, c2, c3 = st.columns([1.45, 1.1, 3.2])
        with c1:
            st.button(
                "＋加入公益项目 ¥9.9",
                key=f"join_campaign_btn_{stage_name}",
                on_click=add_campaign_to_order,
                type="secondary",
                help="可选公益加购，不影响您的房间预订。",
            )
        with c2:
            st.button(
                "暂不参与",
                key=f"skip_campaign_btn_{stage_name}",
                on_click=skip_campaign_order,
                type="secondary",
            )


def maybe_show_nudge():
    if st.session_state.stage in get_nudge_stages():
        show_nudge(st.session_state.stage)


def is_valid_date_range():
    """检查日期是否合法：离店日期必须晚于入住日期。"""
    return st.session_state.check_out > st.session_state.check_in


def show_date_error_if_needed():
    if not is_valid_date_range():
        st.error("离店日期必须晚于入住日期，请重新选择入住和离店时间。")
        return True
    return False


def nights_count():
    if not is_valid_date_range():
        return 0
    nights = (st.session_state.check_out - st.session_state.check_in).days
    return max(nights, 1)


def total_price():
    campaign_price = st.session_state.cart_campaign_price if st.session_state.cart_campaign_added else 0.0
    return st.session_state.room_price * nights_count() + campaign_price


def show_steps():
    html = "<div class='steps'>"
    current_idx = STAGES.index(st.session_state.stage)
    for i, stage in enumerate(STAGES):
        cls = "step-on" if i <= current_idx else "step-off"
        html += f"<span class='{cls}'>{i + 1}. {stage}</span>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def back_button(label="返回上一步"):
    """统一的返回按钮：受试者也可以正常退回上一个页面。"""
    if STAGES.index(st.session_state.stage) > 0:
        if st.button(label, key=f"back_{st.session_state.stage}"):
            prev_stage()
            st.rerun()


def hotel_header():
    st.markdown(
        f"""
        <div class="topbar">
            <div>
                <div class="brand-cn">{HOTEL_CN}</div>
                <div class="brand-en">{HOTEL_EN}</div>
            </div>
            <div>
                <span class="pill">舒适住宿</span>
                <span class="pill">城市出行</span>
                <span class="pill">会员优选</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home():
    hotel_header()
    show_steps()
    st.markdown(
        f"""
        <div class="hero">
            <h1>{HOTEL_CN}预订</h1>
            <p>您已经完成酒店检索，目前正在浏览酒店详情、比较房型并完成最终预订。请根据页面信息选择您希望预订的房型。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.image(HOTEL_IMAGES[0], use_container_width=True)
    st.markdown("<div class='image-note'>酒店外观与公共空间展示</div>", unsafe_allow_html=True)

    st.markdown("<div class='search-card'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.date_input("入住日期", key="check_in")
    with c2:
        st.date_input("离店日期", key="check_out")
    with c3:
        st.number_input("入住人数", min_value=1, max_value=4, key="guest_count")
    with c4:
        st.write("")
        st.write("")
        invalid_date = not is_valid_date_range()
        if st.button("查看酒店", type="primary", use_container_width=True, disabled=invalid_date):
            next_stage()
            st.rerun()
    show_date_error_if_needed()
    st.markdown("</div>", unsafe_allow_html=True)
    maybe_show_nudge()


def render_detail():
    hotel_header()
    show_steps()
    back_button("返回首页")
    st.markdown(
        f"""
        <div class="hotel-card">
            <div class="hotel-name">{HOTEL_CN} <span style="font-size:15px;color:#8a7a6b;">{HOTEL_EN}</span></div>
            <div class="score">4.8 / 5.0 · 住客好评</div>
            <p class="small-muted">酒店位于城市核心区域，交通便利，客房设计温暖简洁，适合商务出行、城市度假与周末短住。</p>
            <span class="pill">近地铁</span><span class="pill">早餐可选</span><span class="pill">免费 Wi-Fi</span><span class="pill">24小时前台</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 酒店图片")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.image(HOTEL_IMAGES[0], use_container_width=True)
    with c2:
        st.image(HOTEL_IMAGES[1], use_container_width=True)
        st.image(HOTEL_IMAGES[2], use_container_width=True)
    st.image(HOTEL_IMAGES[3], use_container_width=True)

    maybe_show_nudge()

    if st.button("查看房型与价格", type="primary"):
        next_stage()
        st.rerun()


def choose_room(room):
    st.session_state.selected_room = room["name"]
    st.session_state.room_price = room["price"]
    log_event("select_room", f"{room['name']} ¥{room['price']}")
    go_stage("订单确认")


def render_rooms():
    hotel_header()
    show_steps()
    back_button("返回酒店详情")
    st.markdown("### 请选择房型")
    maybe_show_nudge()

    for i, room in enumerate(ROOMS):
        st.markdown("<div class='room-card'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1.3, 2.2, 1])
        with c1:
            st.image(room["img"], use_container_width=True)
        with c2:
            st.markdown(f"<div class='room-title'>{room['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p class='small-muted'>{room['desc']}</p>", unsafe_allow_html=True)
            tags_html = "".join([f"<span class='pill'>{tag}</span>" for tag in room.get("tags", [])])
            st.markdown(tags_html, unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='price'>¥{room['price']}</div>", unsafe_allow_html=True)
            st.button(
                "选择并预订",
                key=f"select_room_{i}",
                on_click=choose_room,
                args=(room,),
                type="primary",
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def order_summary(show_actions=True):
    st.markdown("<div class='order-box'>", unsafe_allow_html=True)
    st.markdown("<h3>订单摘要</h3>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>酒店</span><b>{HOTEL_CN}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>房型</span><b>{st.session_state.selected_room or '未选择'}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>入住</span><b>{st.session_state.check_in}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>离店</span><b>{st.session_state.check_out}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>晚数</span><b>{nights_count()}晚</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='cart-line'><span>房费</span><b>¥{st.session_state.room_price * nights_count()}</b></div>", unsafe_allow_html=True)

    if st.session_state.cart_campaign_added:
        st.markdown(
            f"<div class='cart-line'><span>{st.session_state.cart_campaign_name}</span><b>¥{st.session_state.cart_campaign_price}</b></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<span class='success-tag'>公益加购已加入最终结账单</span>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='cart-line'><span>公益加购</span><b>未加入</b></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='total'>合计 ¥{total_price()}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if show_actions and st.session_state.cart_campaign_added:
        st.button("从订单中移除公益加购", key="summary_remove_campaign", on_click=remove_campaign_from_order)


def render_order():
    hotel_header()
    show_steps()
    back_button("返回房型选择")
    if not st.session_state.selected_room:
        st.warning("请先选择房型。")
        if st.button("返回房型选择"):
            go_stage("房型选择")
            st.rerun()
        return
    left, right = st.columns([1.5, 1])
    with left:
        st.markdown("### 确认订单信息")
        st.markdown("请确认您的入住信息、房型和订单金额。")
        maybe_show_nudge()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("返回修改房型"):
                go_stage("房型选择")
                st.rerun()
        with c2:
            if st.button("确认订单并去支付", type="primary", disabled=not is_valid_date_range()):
                next_stage()
                st.rerun()
        show_date_error_if_needed()
    with right:
        order_summary()


def render_payment():
    hotel_header()
    show_steps()
    back_button("返回订单确认")
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown("### 支付页面")
        st.info("这是模拟支付页面，不会产生真实扣款。")
        st.radio("选择支付方式", ["银行卡支付", "支付宝", "微信支付"], horizontal=True)
        if st.button("确认支付", type="primary"):
            st.session_state.paid = True
            log_event("paid", f"支付金额 ¥{total_price()}")
            next_stage()
            st.rerun()
    with right:
        order_summary(show_actions=False)


# =========================
# OTA 界面
# =========================

def ota_shell_start():
    st.markdown("<div class='ota-shell'><div class='ota-inner'>", unsafe_allow_html=True)


def ota_shell_end():
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_ota_home():
    ota_shell_start()
    st.markdown("<div class='ota-header'><span>酒店预订</span><span style='font-size:13px;color:#888;'>筛选 · 地图</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='ota-search'>已检索：城市核心区域 · 1晚 · 1人入住</div>", unsafe_allow_html=True)
    show_steps()
    maybe_show_nudge()

    st.markdown("#### 为您推荐")
    for i, hotel in enumerate(OTA_HOTELS):
        st.markdown("<div class='ota-list-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns([1.1, 2])
        with c1:
            st.image(hotel["img"], use_container_width=True)
        with c2:
            st.markdown(f"<div class='ota-list-title'>{hotel['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<span class='ota-score'>{hotel['score']} {hotel['comment']}</span> <span class='small-muted'>{hotel['distance']}</span>", unsafe_allow_html=True)
            st.caption(f"{hotel['en']} · {hotel['desc']}")
            badges_html = "".join([f"<span class='ota-tag'>{b}</span>" for b in hotel["badges"]])
            st.markdown(badges_html, unsafe_allow_html=True)
            c_price, c_btn = st.columns([1, 1])
            with c_price:
                st.markdown(f"<div class='ota-price'>¥{hotel['price']}起</div>", unsafe_allow_html=True)
            with c_btn:
                if hotel.get("is_target"):
                    if st.button("查看", key=f"view_hotel_{i}", type="primary", use_container_width=True):
                        go_stage("酒店详情")
                        st.rerun()
                else:
                    st.button("查看", key=f"disabled_hotel_{i}", disabled=True, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    ota_shell_end()


def render_ota_detail():
    ota_shell_start()
    st.markdown(f"<div class='ota-header'><span>{HOTEL_CN}</span><span style='font-size:13px;color:#888;'>收藏</span></div>", unsafe_allow_html=True)
    show_steps()
    back_button("返回酒店列表")
    st.image(HOTEL_IMAGES[0], use_container_width=True)
    st.markdown(f"<span class='ota-score'>4.8 棒</span> <span class='small-muted'>{HOTEL_EN} · 舒适型酒店</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<span class='ota-tag'>近地铁</span><span class='ota-tag'>早餐可选</span><span class='ota-tag'>免费Wi-Fi</span><span class='ota-tag'>24小时前台</span>", unsafe_allow_html=True)
    st.caption("位置便利，客房温暖舒适，适合商务出行与休闲住宿。")
    c1, c2 = st.columns(2)
    with c1:
        st.image(HOTEL_IMAGES[1], use_container_width=True)
    with c2:
        st.image(HOTEL_IMAGES[2], use_container_width=True)
    maybe_show_nudge()
    if st.button("选择房型", type="primary", use_container_width=True):
        go_stage("房型选择")
        st.rerun()
    ota_shell_end()


def render_ota_rooms():
    ota_shell_start()
    st.markdown("<div class='ota-header'><span>选择房型</span><span style='font-size:13px;color:#888;'>价格明细</span></div>", unsafe_allow_html=True)
    show_steps()
    back_button("返回酒店详情")
    maybe_show_nudge()
    for i, room in enumerate(ROOMS):
        st.markdown("<div class='ota-room-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.7])
        with c1:
            st.image(room["img"], use_container_width=True)
        with c2:
            st.markdown(f"**{room['name']}**")
            st.caption(room["desc"])
            st.markdown(" ".join([f"`{tag}`" for tag in room.get("tags", [])]))
            st.markdown(f"<div class='ota-price'>¥{room['price']}</div>", unsafe_allow_html=True)
            st.button(
                "立即预订",
                key=f"ota_room_{i}",
                on_click=choose_room,
                args=(room,),
                type="primary",
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    ota_shell_end()


def render_ota_order():
    ota_shell_start()
    show_steps()
    back_button("返回房型选择")
    if not st.session_state.selected_room:
        st.warning("请先选择房型。")
        if st.button("返回房型选择"):
            go_stage("房型选择")
            st.rerun()
        ota_shell_end()
        return
    st.markdown("### 确认订单")
    maybe_show_nudge()
    order_summary()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("返回修改"):
            go_stage("房型选择")
            st.rerun()
    with c2:
        if st.button("去支付", type="primary", disabled=not is_valid_date_range()):
            next_stage()
            st.rerun()
    show_date_error_if_needed()
    ota_shell_end()


def render_ota_payment():
    ota_shell_start()
    show_steps()
    back_button("返回订单确认")
    st.markdown("### 收银台")
    st.info("这是模拟支付页面，不会产生真实扣款。")
    order_summary(show_actions=False)
    st.radio("支付方式", ["支付宝", "微信支付", "银行卡"], horizontal=True)
    if st.button("确认支付", type="primary", use_container_width=True):
        st.session_state.paid = True
        log_event("paid", f"支付金额 ¥{total_price()}")
        next_stage()
        st.rerun()
    ota_shell_end()


# =========================
# 问卷
# =========================

def slider_value_to_number(value):
    """把 '1 非常不同意' 这样的滑块文本转成数字，方便后续导出数据分析。"""
    try:
        return int(str(value).split()[0])
    except Exception:
        return value


def likert(label, key):
    options = [
        "1 非常不同意",
        "2 不同意",
        "3 有点不同意",
        "4 一般",
        "5 有点同意",
        "6 同意",
        "7 非常同意",
    ]
    value = st.select_slider(label, options=options, value="4 一般", key=key)
    return slider_value_to_number(value)


def frequency_check(label, key):
    options = [
        "1 非常少",
        "2 少",
        "3 有些少",
        "4 适中",
        "5 有些多",
        "6 多",
        "7 非常多",
    ]
    value = st.select_slider(label, options=options, value="4 适中", key=key)
    return slider_value_to_number(value)


def recall_check(label, key):
    options = ["0次", "1次", "2次", "3次", "4次"]
    value = st.select_slider(label, options=options, value="2次", key=key)
    return int(value.replace("次", ""))


def motive_scale(label, key):
    options = [
        "1 完全出于酒店自身利益",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7 完全出于社会责任",
    ]
    value = st.select_slider(label, options=options, value="4", key=key)
    return slider_value_to_number(value)


def render_survey():
    hotel_header()
    show_steps()
    st.markdown("### 预订体验问卷")
    st.markdown("请根据刚才的网页浏览与预订体验回答以下问题。")

    mc_frequency = frequency_check("1. 您认为酒店的公益营销活动信息的展示频率如何？", "mc_frequency")
    mc_recall_count = recall_check("2. 您是否还记得在刚才的网页中遇到过几次公益营销界面？", "mc_recall_count")

    reactance_1 = likert("3. 这条酒店APP推送的公益信息限制了我的选择自由。", "reactance_1")
    reactance_2 = likert("4. 这条酒店APP推送的公益信息试图操控我。", "reactance_2")
    reactance_3 = likert("5. 这条酒店APP推送的公益信息似乎替我做了决定。", "reactance_3")
    reactance_4 = likert("6. 这条酒店APP推送的公益信息让我感到有些压力。", "reactance_4")
    reactance_5 = likert("7. 我觉得这条酒店APP推送的公益信息试图支配我的行为。", "reactance_5")
    reactance_6 = likert("8. 我感觉这条酒店APP推送的公益信息想让我按照它的意图去做。", "reactance_6")
    reactance_7 = likert("9. 我感到这条酒店APP推送的公益信息让我被迫采取某种行动。", "reactance_7")

    fit_1 = likert("10. 酒店公益信息提及的动物公仔，与支持动物救助事业的公益目标很契合。", "fit_1")
    fit_2 = likert("11. 酒店公益信息提及的动物公仔与动物救助事业紧密相连。", "fit_2")
    fit_3 = likert("12. 用动物公仔销售的收益支持动物救助事业，是顺理成章且极为合适的公益举措。", "fit_3")

    altruism_1 = motive_scale("13. 您认为这项公益活动在多大程度上是出于酒店自身利益的动机，还是出于对社会责任的关注？", "altruism_1")
    altruism_2 = motive_scale("14. 您认为这项公益活动在多大程度上是出于追求利润的动机，还是出于社会责任的动机？", "altruism_2")
    altruism_3 = motive_scale("15. 您认为这项公益活动在多大程度上是出于自我导向（利己）的动机，还是出于利他主义的动机？", "altruism_3")

    st.markdown("---")
    birth_year = st.number_input("16. 您的出生年份是", min_value=1940, max_value=date.today().year, value=2000, step=1, key="birth_year")
    gender = st.radio("17. 您的性别是", options=["男", "女"], horizontal=True, key="gender")

    if not st.session_state.survey_submitted:
        if st.button("提交问卷", type="primary"):
            result = {
                "submit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "participant_id": st.session_state.participant_id,
                "interface_mode": st.session_state.interface_mode,
                "nudge_frequency": st.session_state.nudge_frequency,
                "product_cause_fit": st.session_state.product_cause_fit,
                "altruistic_motivation": st.session_state.altruistic_motivation,
                "nudge_seen": st.session_state.nudge_seen,
                "selected_room": st.session_state.selected_room,
                "room_price": st.session_state.room_price,
                "joined_campaign": st.session_state.cart_campaign_added,
                "campaign_product_name": st.session_state.cart_campaign_name,
                "donation_amount": st.session_state.cart_campaign_price if st.session_state.cart_campaign_added else 0,
                "total_price": total_price(),
                "paid": st.session_state.paid,
                "mc_frequency": mc_frequency,
                "mc_recall_count": mc_recall_count,
                "reactance_1": reactance_1,
                "reactance_2": reactance_2,
                "reactance_3": reactance_3,
                "reactance_4": reactance_4,
                "reactance_5": reactance_5,
                "reactance_6": reactance_6,
                "reactance_7": reactance_7,
                "fit_1": fit_1,
                "fit_2": fit_2,
                "fit_3": fit_3,
                "altruism_1": altruism_1,
                "altruism_2": altruism_2,
                "altruism_3": altruism_3,
                "birth_year": birth_year,
                "gender": gender,
            }
            save_result_to_csv(result)
            save_events_to_csv()
            st.session_state.survey_submitted = True
            st.success("问卷已提交，感谢您的参与！")
            st.rerun()
    else:
        st.success("问卷已提交，感谢您的参与！")


# =========================
# 页面分发
# =========================

def render_ota_wrapper():
    stage = st.session_state.stage
    if stage == "浏览首页":
        render_ota_home()
    elif stage == "酒店详情":
        render_ota_detail()
    elif stage == "房型选择":
        render_ota_rooms()
    elif stage == "订单确认":
        render_ota_order()
    elif stage == "支付页面":
        render_ota_payment()
    elif stage == "完成问卷":
        render_survey()


def render_participant_app():
    stage = st.session_state.stage
    if st.session_state.interface_mode == "OTA界面":
        render_ota_wrapper()
        return
    if stage == "浏览首页":
        render_home()
    elif stage == "酒店详情":
        render_detail()
    elif stage == "房型选择":
        render_rooms()
    elif stage == "订单确认":
        render_order()
    elif stage == "支付页面":
        render_payment()
    elif stage == "完成问卷":
        render_survey()


def render_admin_panel():
    st.markdown("<div class='main-title'>后台管理页面</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>本页面用于设置实验条件、预览受试者页面，并下载实验数据。受试者默认不会看到这里。</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.header("后台控制台")
        st.caption("公开测试时，不要把带 ?admin=1 的链接发给受试者。")
        st.session_state.interface_mode = st.selectbox(
            "界面类型",
            ["酒店官网界面", "OTA界面"],
            index=["酒店官网界面", "OTA界面"].index(st.session_state.interface_mode),
        )
        st.session_state.nudge_frequency = st.selectbox(
            "数字助推频率",
            list(DEFAULT_STAGE_MAP.keys()),
            index=list(DEFAULT_STAGE_MAP.keys()).index(st.session_state.nudge_frequency),
        )
        st.session_state.product_cause_fit = st.selectbox(
            "产品-公益匹配度",
            ["高匹配：毛绒公仔 × 濒危动物保护", "低匹配：明信片 × 濒危动物保护"],
            index=["高匹配：毛绒公仔 × 濒危动物保护", "低匹配：明信片 × 濒危动物保护"].index(st.session_state.product_cause_fit),
        )
        st.session_state.altruistic_motivation = st.selectbox(
            "感知利他动机",
            ["高利他动机：全部收益捐出", "低利他动机：公益合作运营推广"],
            index=["高利他动机：全部收益捐出", "低利他动机：公益合作运营推广"].index(st.session_state.altruistic_motivation),
        )
        st.divider()
        st.write("当前阶段：", st.session_state.stage)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("上一步"):
                prev_stage()
                st.rerun()
        with c2:
            if st.button("下一步"):
                next_stage()
                st.rerun()
        if st.button("重置实验", type="secondary"):
            reset_experiment()

    tab1, tab2, tab3 = st.tabs(["受试者页面预览", "数据下载", "使用说明"])
    with tab1:
        render_participant_app()
    with tab2:
        st.markdown("### 实验数据")
        if DATA_PATH.exists():
            df = pd.read_csv(DATA_PATH)
            st.dataframe(df, use_container_width=True)
            st.download_button("下载实验结果 CSV", data=DATA_PATH.read_bytes(), file_name="experiment_data.csv", mime="text/csv")
        else:
            st.info("目前还没有实验结果数据。")
        st.markdown("### 行为日志")
        if EVENT_PATH.exists():
            event_df = pd.read_csv(EVENT_PATH)
            st.dataframe(event_df, use_container_width=True)
            st.download_button("下载行为日志 CSV", data=EVENT_PATH.read_bytes(), file_name="experiment_events.csv", mime="text/csv")
        else:
            st.info("目前还没有行为日志。")
    with tab3:
        st.markdown(
            """
            **受试者链接：** 直接使用普通网页链接，不带 `?admin=1`。  
            **后台链接：** 在网页链接后加 `?admin=1`。  

            例如：
            - 受试者：`https://your-app.streamlit.app`
            - 后台：`https://your-app.streamlit.app?admin=1`

            当前版本为测试版。正式实验前建议继续加入：自动随机分组、最短作答时间、注意力检测、重复提交限制。

            图片说明：当前使用公开图库链接。正式实验时建议替换为统一风格的本地图片，避免外部网络导致图片加载失败。
            """
        )


if is_admin_page():
    render_admin_panel()
else:
    render_participant_app()
