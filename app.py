import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.title("收入计算器_阶梯定价策略")

# 初始化状态
if 'breakpoints' not in st.session_state:
    st.session_state.breakpoints = []
if 'prices' not in st.session_state:
    st.session_state.prices = []
if 'history' not in st.session_state:
    st.session_state.history = []
if 'people' not in st.session_state:
    st.session_state.people = 0

# 输入参数
with st.sidebar:
    st.header("输入参数")
    
    # 分段点输入
    bp_text = st.text_input("人数分段点 (用逗号分隔)", "10,50,100")
    # 价格输入
    p_text = st.text_input("对应价格 (用逗号分隔)", "100,80,60")
    
    # 验证按钮
    if st.button("确认输入"):
        try:
            # 获取分段点
            st.session_state.breakpoints = [float(x.strip()) for x in bp_text.split(",") if x.strip()]
            # 获取价格
            st.session_state.prices = [float(x.strip()) for x in p_text.split(",") if x.strip()]
            
            # 检查长度是否匹配
            if len(st.session_state.breakpoints) != len(st.session_state.prices):
                st.error("人数分段点和价格分段的长度必须相同！")
                st.session_state.breakpoints = []
                st.session_state.prices = []
            # 检查分段点是否按顺序排列
            elif st.session_state.breakpoints != sorted(st.session_state.breakpoints):
                st.error("人数分段点必须按从小到大顺序排列！")
                st.session_state.breakpoints = []
                st.session_state.prices = []
            else:
                st.success("输入数据有效！现在您可以使用滑块或输入框来调整人数。")
                st.session_state.history = []
        except ValueError:
            st.error("请输入有效的数字！")
            st.session_state.breakpoints = []
            st.session_state.prices = []
    
    # 实际人数输入
    st.session_state.people = st.slider("实际人数", 0, 1000, 50)

# 计算收入
def calculate_income(people):
    if not st.session_state.breakpoints or not st.session_state.prices:
        return 0, 0, 0
    
    # 确定所在区间
    interval_index = 0
    for i, bp in enumerate(st.session_state.breakpoints):
        if people >= bp:
            interval_index = i
        else:
            break
    
    # 获取对应价格
    price = st.session_state.prices[interval_index]
    
    # 计算收入
    income = people * price
    
    # 记录历史
    st.session_state.history.append((people, income))
    if len(st.session_state.history) > 100:
        st.session_state.history.pop(0)
    
    return income, interval_index, price

# 计算结果
if st.session_state.breakpoints and st.session_state.prices:
    income, interval_index, price = calculate_income(st.session_state.people)
    
    # 显示结果
    st.header("计算结果")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("当前人数", st.session_state.people)
    with col2:
        if interval_index == len(st.session_state.breakpoints) - 1:
            interval_text = f"{st.session_state.breakpoints[interval_index]}人以上"
        else:
            interval_text = f"{st.session_state.breakpoints[interval_index]}～{st.session_state.breakpoints[interval_index+1]}人"
        st.metric("所在区间", interval_text)
    with col3:
        st.metric("适用价格", f"¥{price:.2f}/人")
    with col4:
        st.metric("总收入", f"¥{income:.2f}", delta_color="off")
    
    # 绘制图表
    st.header("收入变化曲线")
    fig, ax = plt.subplots(figsize=(10, 4))
    
    if st.session_state.history:
        # 提取历史数据
        people_vals = [h[0] for h in st.session_state.history]
        income_vals = [h[1] for h in st.session_state.history]
        
        # 绘制散点图
        ax.scatter(people_vals, income_vals, color='blue', alpha=0.5, label='收入记录')
        
        # 如果有足够的数据点，绘制折线图
        if len(st.session_state.history) > 1:
            # 按人数排序
            sorted_data = sorted(st.session_state.history, key=lambda x: x[0])
            sorted_people = [d[0] for d in sorted_data]
            sorted_income = [d[1] for d in sorted_data]
            
            # 绘制折线
            ax.plot(sorted_people, sorted_income, 'r-', linewidth=2, label='趋势线')
        
        # 添加当前点标记
        ax.scatter(st.session_state.people, income, 
                  color='green', s=100, edgecolor='black', 
                  zorder=5, label='当前点')
        
        # 添加分隔线
        for i, bp in enumerate(st.session_state.breakpoints):
            if i == 0:
                continue
            ax.axvline(x=bp, color='gray', linestyle='--', alpha=0.5)
            ax.text(bp, min(income_vals), f"分段{i}", 
                   ha='center', va='top', backgroundcolor='white')
        
        # 自动调整坐标轴范围
        if people_vals:
            padding = (max(people_vals) - min(people_vals)) * 0.05
            ax.set_xlim(min(people_vals) - padding, max(people_vals) + padding)
    
    # 设置图表属性
    ax.set_title("收入变化曲线")
    ax.set_xlabel("人数")
    ax.set_ylabel("收入(元)")
    ax.grid(True)
    ax.legend()
    
    st.pyplot(fig)
else:
    st.warning("请在左侧边栏输入有效的分段点和价格")