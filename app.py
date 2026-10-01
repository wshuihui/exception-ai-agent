import streamlit as st
from openai import OpenAI
import json
import time

# ========== 页面配置 ==========
st.set_page_config(page_title="例外 · 智能客服", page_icon="◯", layout="wide", initial_sidebar_state="expanded")

# ========== 高奢东方美学样式 ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;500;600&display=swap');
.stApp { background: linear-gradient(180deg, #F7F2EA 0%, #F0E9DD 50%, #EDE5D6 100%); background-attachment: fixed; }
.hero { text-align: center; padding: 48px 0 36px 0; position: relative; }
.hero::after { content: ''; display: block; width: 60px; height: 1px; background: linear-gradient(90deg, transparent, #B89968, transparent); margin: 28px auto 0; }
.hero h1 { font-family: 'Noto Serif SC', '宋体', serif; font-size: 52px; font-weight: 300; color: #2A2A2A; letter-spacing: 24px; margin: 0; text-indent: 24px; }
.hero .en { font-family: 'Noto Serif SC', serif; font-size: 12px; color: #9A8B72; letter-spacing: 6px; margin-top: 14px; }
.hero .slogan { font-family: 'Noto Serif SC', serif; font-size: 14px; color: #7A6E5D; letter-spacing: 4px; margin-top: 18px; font-weight: 300; }
.side-card { background: rgba(255,253,248,0.55); backdrop-filter: blur(10px); border-radius: 4px; padding: 22px 20px; margin-bottom: 20px; border: 1px solid rgba(184,153,104,0.2); border-left: 2px solid #B89968; }
.side-card h3 { font-family: 'Noto Serif SC', serif; font-size: 15px; color: #5C4F3E; letter-spacing: 3px; margin: 0 0 14px 0; font-weight: 500; }
.side-card p, .side-card li { font-size: 13px; color: #6B5F4E; line-height: 2; margin: 0; }
div.stButton > button { background: rgba(255,253,248,0.6) !important; border: 1px solid rgba(184,153,104,0.3) !important; color: #5C4F3E !important; border-radius: 2px !important; padding: 9px 14px !important; font-size: 13px !important; letter-spacing: 1px; transition: all 0.4s ease !important; width: 100%; text-align: left; }
div.stButton > button:hover { background: #B89968 !important; color: #fff !important; border-color: #B89968 !important; transform: translateX(4px); }
.user-bubble { background: #3D3830; color: #F5EFE6; padding: 14px 20px; border-radius: 2px 16px 16px 16px; margin: 14px 0; max-width: 78%; margin-left: auto; font-size: 14.5px; line-height: 1.8; box-shadow: 0 4px 20px rgba(61,56,48,0.15); }
.ai-bubble { background: rgba(255,253,248,0.85); backdrop-filter: blur(8px); color: #3A342C; padding: 16px 22px; border-radius: 16px 2px 16px 16px; margin: 14px 0; max-width: 88%; font-size: 14.5px; line-height: 1.9; box-shadow: 0 4px 24px rgba(92,79,62,0.08); border: 1px solid rgba(184,153,104,0.15); }
.ai-bubble strong { color: #8B6F47; }
.tool-status { background: rgba(184,153,104,0.1); border-left: 3px solid #B89968; padding: 10px 16px; margin: 10px 0; font-size: 13px; color: #7A6E5D; border-radius: 0 4px 4px 0; max-width: 60%; }
.stChatInput { padding-bottom: 28px; }
.stChatInput input { background: rgba(255,253,248,0.7) !important; border: 1px solid rgba(184,153,104,0.3) !important; border-radius: 2px !important; color: #3A342C !important; font-size: 14px !important; }
.stChatInput input:focus { border-color: #B89968 !important; box-shadow: 0 0 0 3px rgba(184,153,104,0.1) !important; }
.stChatInput button { background: #B89968 !important; border: none !important; }
.stChatInput button:hover { background: #9A7E50 !important; }
#MainMenu { visibility: hidden; } footer { visibility: hidden; } header { visibility: hidden; }
.block-container { padding-top: 0; padding-bottom: 0; max-width: 1400px; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: transparent; } ::-webkit-scrollbar-thumb { background: rgba(184,153,104,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ========== 初始化 ==========
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
except:
    api_key = "你的key"  # 本地调试用，部署后线上会用secrets里的
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


with open("例外服装智能客服知识库.md", "r", encoding="utf-8") as f:
    knowledge_base = f.read()

# ========== 商品数据 ==========
products = [
    {"id": "EX-SS26-V01", "name": "素白纯棉小高领背心", "price": 798, "keywords": ["素白", "背心", "小高领", "纯棉背心", "白背心"], "stock": {"XS": 15, "S": 23, "M": 18, "L": 8, "XL": 3}},
    {"id": "EX-SS26-S02", "name": "冉竹丝麻新中式衬衫", "price": 1298, "keywords": ["冉竹", "衬衫", "新中式", "丝麻衬衫", "衬衣"], "stock": {"XS": 5, "S": 12, "M": 20, "L": 15, "XL": 6}},
    {"id": "EX-AW25-K03", "name": "轻舟丝毛针织开衫", "price": 1598, "keywords": ["轻舟", "开衫", "针织", "丝毛", "外套", "毛衣"], "stock": {"XS": 8, "S": 15, "M": 25, "L": 18, "XL": 10}},
    {"id": "EX-SS26-P05", "name": "子也棉麻阔腿裤", "price": 998, "keywords": ["子也", "阔腿裤", "棉麻裤", "裤子", "长裤"], "stock": {"XS": 10, "S": 18, "M": 22, "L": 12, "XL": 5}},
    {"id": "EX-SS26-D04", "name": "缭绫非遗工艺连衣裙", "price": 4998, "keywords": ["缭绫", "连衣裙", "非遗", "裙子", "长裙"], "stock": {"S": 1, "M": 0, "L": 2}},
]

# ========== 门店数据 ==========
stores = {
    "广州": [
        {"name": "太古汇店", "address": "天河区天河路383号太古汇M层M43", "phone": "020-38682156", "hours": "10:00-22:00"},
        {"name": "天环广场店", "address": "天河区天河路218号天环广场L2层L206", "phone": "020-38553348", "hours": "10:00-22:00"},
        {"name": "K11店", "address": "天河区珠江东路6号K11购物艺术中心L3层", "phone": "020-88832267", "hours": "10:00-22:00"},
    ],
    "北京": [
        {"name": "SKP店", "address": "朝阳区建国路87号SKP 3层D3012", "phone": "010-65331526", "hours": "10:00-22:00"},
        {"name": "三里屯店", "address": "朝阳区三里屯路19号太古里南区S2-12", "phone": "010-64176685", "hours": "10:00-22:00"},
    ],
    "上海": [
        {"name": "恒隆广场店", "address": "静安区南京西路1266号恒隆广场3楼313", "phone": "021-62886635", "hours": "10:00-22:00"},
        {"name": "新天地店", "address": "黄浦区马当路245号新天地时尚L1层", "phone": "021-63857789", "hours": "10:00-22:00"},
    ],
    "深圳": [{"name": "万象城店", "address": "罗湖区宝安南路1881号万象城3楼389", "phone": "0755-82668857", "hours": "10:00-22:00"}],
    "成都": [{"name": "IFS店", "address": "锦江区红星路三段1号IFS国际金融中心L3层", "phone": "028-86665523", "hours": "10:00-22:00"}],
    "杭州": [{"name": "万象城店", "address": "江干区富春路701号万象城2楼L268", "phone": "0571-88996678", "hours": "10:00-22:00"}],
}

# ========== 会员数据 ==========
members = {
    "13800138000": {"name": "李女士", "level": "黑卡会员", "points": 12580, "benefits": "9折优惠、免费改衣、生日双倍积分、专属穿搭顾问、优先预约"},
    "13900139000": {"name": "王女士", "level": "金卡会员", "points": 5620, "benefits": "95折优惠、生日礼、免费改衣"},
    "13700137000": {"name": "张女士", "level": "银卡会员", "points": 1850, "benefits": "98折优惠、生日礼"},
}

# ========== 订单数据 ==========
orders = {
    "ORD202609001": {"status": "已发货", "product": "素白纯棉小高领背心", "size": "M", "price": 798, "tracking": "SF1234567890"},
    "ORD202609002": {"status": "待发货", "product": "冉竹丝麻新中式衬衫", "size": "L", "price": 1298, "tracking": None},
    "ORD202609003": {"status": "已完成", "product": "轻舟丝毛针织开衫", "size": "M", "price": 1598, "tracking": "SF9876543210"},
}

# ========== 物流数据 ==========
logistics = {
    "SF1234567890": [
        {"time": "2026-09-28 14:30", "status": "快件已到达【广州天河集散中心】"},
        {"time": "2026-09-28 09:15", "status": "快件已从【广州白云集散中心】发出"},
        {"time": "2026-09-27 20:00", "status": "商家已发货，快件已揽收"},
    ],
    "SF9876543210": [
        {"time": "2026-09-25 16:20", "status": "快件已签收，签收人：本人"},
        {"time": "2026-09-25 08:30", "status": "快件正在派送中，快递员：张师傅 138****5678"},
        {"time": "2026-09-24 22:00", "status": "快件已到达【广州天河集散中心】"},
    ],
}

return_orders = []
fitting_bookings = []

# ========== 工具函数 ==========
def find_product(query):
    query = query.strip()
    for p in products:
        if p["id"].upper() == query.upper(): return p
    for p in products:
        if query in p["name"]: return p
        for kw in p["keywords"]:
            if kw in query: return p
    return None

def check_inventory(product_name, size=None):
    p = find_product(product_name)
    if not p:
        return f"抱歉，没有找到与「{product_name}」相关的商品。您可以告诉我商品名称，比如'素白背心''冉竹衬衫'，我帮您查询~"
    if size:
        size = size.upper().replace("码", "").strip()
        if size not in p["stock"]:
            return f"「{p['name']}」没有{size}码哦，可选尺码有：{'、'.join(p['stock'].keys())}"
        n = p["stock"][size]
        if n > 0:
            return f"「{p['name']}」的{size}码目前有货，库存{n}件，售价{p['price']}元。这款是经典款，面料舒适版型好，很受欢迎呢~"
        else:
            return f"非常抱歉，「{p['name']}」的{size}码暂时缺货了。您可以留下联系方式，到货后我们会第一时间通知您~"
    stock_info = "，".join([f"{k}码{v}件" for k, v in p["stock"].items()])
    return f"「{p['name']}」各尺码库存：{stock_info}，售价{p['price']}元。请问您穿什么码呢？"

def check_order(order_id):
    order_id = order_id.strip().upper()
    if order_id not in orders:
        return f"没有找到订单{order_id}，请确认订单号是否正确（通常以ORD开头）"
    o = orders[order_id]
    r = f"订单{order_id}情况：\n- **状态**：{o['status']}\n- **商品**：{o['product']}（{o['size']}码）\n- **金额**：{o['price']}元"
    if o["tracking"]: r += f"\n- **快递单号**：{o['tracking']}"
    return r

def create_return(order_id, reason):
    order_id = order_id.strip().upper()
    if order_id not in orders:
        return f"没有找到订单{order_id}，无法创建退换货申请"
    rid = f"RET{len(return_orders)+1:04d}"
    return_orders.append({"id": rid, "order": order_id, "reason": reason})
    return f"已为您创建退换货申请：\n- **申请单号**：{rid}\n- **退换原因**：{reason}\n我们会在24小时内审核，请保持电话畅通。审核通过后发送退货地址，收到商品后3-5个工作日处理。"

def find_store(city):
    city = city.strip().replace("市", "").replace("省", "")
    if city not in stores:
        return f"抱歉，{city}目前还没有例外门店。我们目前在广州、北京、上海、深圳、成都、杭州等城市设有门店，您看哪个城市方便呢？"
    store_list = stores[city]
    r = f"为您找到{city}的{len(store_list)}家例外门店：\n\n"
    for i, s in enumerate(store_list, 1):
        r += f"**{i}. {s['name']}**\n- 地址：{s['address']}\n- 电话：{s['phone']}\n- 营业时间：{s['hours']}\n\n"
    r += f"您也可以告诉我您所在的区域，我帮您推荐最近的门店~需要预约试衣吗？"
    return r

def check_member(phone):
    phone = phone.strip()
    if phone not in members:
        return f"没有找到手机号{phone}的会员信息。您可以到门店或官网免费注册会员，首单即享98折优惠哦~"
    m = members[phone]
    return f"您好{m['name']}！您的会员信息：\n- **会员等级**：{m['level']}\n- **当前积分**：{m['points']}分\n- **专属权益**：{m['benefits']}\n\n积分可以在消费时抵扣现金，100积分=1元哦~"

def create_fitting(store, date, name, phone):
    booking_id = f"FIT{len(fitting_bookings)+1:04d}"
    fitting_bookings.append({"id": booking_id, "store": store, "date": date, "name": name, "phone": phone})
    return f"已为您预约试衣成功~\n- **预约号**：{booking_id}\n- **门店**：{store}\n- **日期**：{date}\n- **预约人**：{name}\n- **联系电话**：{phone}\n\n请在预约时间到店，报预约号即可。到店前我们会短信提醒您，期待您的光临~"

def check_logistics(tracking_number):
    tracking_number = tracking_number.strip().upper()
    if tracking_number not in logistics:
        return f"没有找到快递单号{tracking_number}的物流信息，请确认单号是否正确。如果刚发货，物流信息可能还没更新，建议半天后再查~"
    tracks = logistics[tracking_number]
    r = f"快递单号{tracking_number}物流轨迹：\n\n"
    for t in tracks:
        r += f"📍 **{t['time']}**\n{t['status']}\n\n"
    return r

tools_map = {
    "check_inventory": check_inventory, "check_order": check_order, "create_return": create_return,
    "find_store": find_store, "check_member": check_member, "create_fitting": create_fitting, "check_logistics": check_logistics,
}

tools = [
    {"type": "function", "function": {"name": "check_inventory", "description": "查询商品库存，用户问某款商品有没有货、某个尺码有没有时调用。product_name是商品名称或简称", "parameters": {"type": "object", "properties": {"product_name": {"type": "string"}, "size": {"type": "string"}}, "required": ["product_name"]}}},
    {"type": "function", "function": {"name": "check_order", "description": "查询订单状态，用户问订单到哪了、发货了吗时调用", "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {"name": "create_return", "description": "创建退换货申请，用户说要退货换货时调用", "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}, "reason": {"type": "string"}}, "required": ["order_id", "reason"]}}},
    {"type": "function", "function": {"name": "find_store", "description": "查询门店地址，用户问某城市有没有门店、门店在哪、地址电话时调用", "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "城市名，如广州、北京"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "check_member", "description": "查询会员信息，用户报手机号查会员等级、积分、权益时调用", "parameters": {"type": "object", "properties": {"phone": {"type": "string", "description": "手机号"}}, "required": ["phone"]}}},
    {"type": "function", "function": {"name": "create_fitting", "description": "预约门店试衣，用户说要预约试衣、到店试穿时调用", "parameters": {"type": "object", "properties": {"store": {"type": "string"}, "date": {"type": "string"}, "name": {"type": "string"}, "phone": {"type": "string"}}, "required": ["store", "date", "name", "phone"]}}},
    {"type": "function", "function": {"name": "check_logistics", "description": "查询物流轨迹，用户问快递到哪了、物流状态时调用", "parameters": {"type": "object", "properties": {"tracking_number": {"type": "string", "description": "快递单号"}}, "required": ["tracking_number"]}}},
]

system_prompt = f"""你是例外（EXCEPTION de MIXMIND）品牌的专属智能客服"小例"。例外1996年创立，中国原创设计师品牌，东方美学+天然面料，中高端定位。品牌理念："女人没有缺点只有特点，衣服是表达个人意识与品味素养的媒介。"

你专业、温柔、有品味，像懂时尚的闺蜜在聊天。

【品牌知识库】
{knowledge_base}

【回答规则】
1. 基于知识库回答，不编造
2. 回答详细有温度，主动补充相关信息，可用"您好呀""呢""哦""~"
3. 查库存/订单/退换货/门店/会员/预约/物流请调用工具
4. 只回答服装相关问题
5. 用Markdown格式，适当加粗和列表
6. 回答结束可主动推荐相关服务
"""

# ========== 流式输出函数 ==========
def stream_response(messages):
    """调用API流式生成，逐字返回"""
    try:
        stream = client.chat.completions.create(model="deepseek-chat", messages=messages, stream=True)
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"抱歉，网络出了点小问题：{str(e)}，请稍后再试~"

def trim_history(messages, max_tokens=8000):
    """简单的历史截断，防止上下文过长（保留system+最近对话）"""
    if len(messages) <= 12: return messages
    return [messages[0]] + messages[-10:]

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown('<div class="side-card"><h3>关 于 例 外</h3><p>创立于1996年，中国现存时间最长的原创设计师品牌。于淡雅中藏风骨，于极简间显气韵。</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-card"><h3>服 务 内 容</h3><p>· 产品咨询与推荐<br>· 面料知识与保养<br>· 尺码穿搭建议<br>· <b>实时库存查询</b><br>· <b>订单物流追踪</b><br>· <b>退换货申请</b><br>· <b>门店查询与预约</b><br>· <b>会员权益查询</b></p></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-card"><h3>试 试 问 我</h3></div>', unsafe_allow_html=True)
    examples = [
        "有什么白色款式推荐？",
        "素白背心M码有货吗？",
        "真丝衣服可以机洗吗？",
        "广州哪里有门店？",
        "帮我查ORD202609001订单",
        "手机号13800138000查会员",
        "SF1234567890物流到哪了",
        "缭绫连衣裙是什么面料？",
    ]
    for ex in examples:
        if st.button(ex, key=ex):
            st.session_state.pending = ex

# ========== 主区域 ==========
st.markdown('<div class="hero"><h1>例 外</h1><div class="en">EXCEPTION de MIXMIND</div><div class="slogan">衣 以 载 道 · 例 外 而 生</div></div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "pending" not in st.session_state: st.session_state.pending = None
if "greeted" not in st.session_state: st.session_state.greeted = False

if not st.session_state.greeted and not st.session_state.messages:
    welcome = "您好呀~欢迎来到例外，我是您的专属客服小例🧥\n\n我可以帮您解答产品咨询、面料保养、尺码建议，还能**实时查库存、查订单物流、办理退换货、查询门店、预约试衣、查会员权益**。有什么想了解的，随时跟我说哦~"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    st.session_state.greeted = True

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

user_input = st.chat_input("请输入您的问题...", key="chat")
if st.session_state.pending:
    user_input = st.session_state.pending
    st.session_state.pending = None

if user_input and user_input.strip():
    if len(user_input) > 500: user_input = user_input[:500] + "..."
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f'<div class="user-bubble">{user_input}</div>', unsafe_allow_html=True)
    
    messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages: messages.append(m)
    messages = trim_history(messages)
    
    try:
        # 第一次调用：判断是否需要工具
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, tools=tools, tool_choice="auto")
        msg = resp.choices[0].message
        
        if msg.tool_calls:
            # 显示工具调用状态
            tool_status = st.empty()
            tool_names = {"check_inventory": "查询库存", "check_order": "查询订单", "create_return": "办理退换货", "find_store": "查询门店", "check_member": "查询会员", "create_fitting": "预约试衣", "check_logistics": "查询物流"}
            status_text = "正在为您" + "、".join([tool_names.get(tc.function.name, tc.function.name) for tc in msg.tool_calls]) + "..."
            tool_status.markdown(f'<div class="tool-status">⏳ {status_text}</div>', unsafe_allow_html=True)
            
            # 执行所有工具
            for tc in msg.tool_calls:
                result = tools_map[tc.function.name](**json.loads(tc.function.arguments))
                messages.append(msg)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            
            tool_status.empty()
            
            # 第二次调用：流式输出最终回答
            reply_placeholder = st.empty()
            full_reply = ""
            for token in stream_response(messages):
                full_reply += token
                reply_placeholder.markdown(f'<div class="ai-bubble">{full_reply}▌</div>', unsafe_allow_html=True)
            reply_placeholder.markdown(f'<div class="ai-bubble">{full_reply}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
        else:
            # 不需要工具，流式输出回答
            reply_placeholder = st.empty()
            full_reply = ""
            for token in stream_response(messages):
                full_reply += token
                reply_placeholder.markdown(f'<div class="ai-bubble">{full_reply}▌</div>', unsafe_allow_html=True)
            reply_placeholder.markdown(f'<div class="ai-bubble">{full_reply}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
    
    except Exception as e:
        error_msg = f"抱歉，出了点小问题：{str(e)}\n\n您可以稍后再试，或者换个问法~"
        st.markdown(f'<div class="ai-bubble">{error_msg}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown('<div style="text-align:center;padding:20px 0 10px;color:#9A8B72;font-size:11px;letter-spacing:3px;border-top:1px solid rgba(184,153,104,0.15);margin-top:30px;">EXCEPTION de MIXMIND · 智能客服系统 · AI Agent 驱动</div>', unsafe_allow_html=True)
