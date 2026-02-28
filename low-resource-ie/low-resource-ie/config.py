# config.py
import argparse
from typing import Optional

# 全局配置对象（在导入时初始化为 None）
args: Optional[argparse.Namespace] = None

def init_config():
    global args
    if args is not None:
        return  # 已初始化
    figure_array=[
        # === 原有基础化学与矿床属性 ===
        '地球化学异常元素符号',
        '成矿深度',
        '成矿温度',
        '其他温度',
        '成矿时间或年代',
        '其他时间或年代',
        '矿体尺寸',
        '元素比值',
        '公式',
        '其他数值或符号',
        '蚀变带宽度',

        # === 新增：地质体物性与几何特征 (来自本体文件) ===
        '地质体密度特征',     # 描述重力场中的密度表现
        '地质体电性特征',     # 描述电阻率、电导率
        '地质体磁性特征',     # 描述磁化率或磁异常
        '地质体埋深范围',     # 描述地下空间中的埋深区间
        '地质体形态特征',     # 描述层状、块状等几何形态
        '地质体空间尺度',     # 描述空间上的整体尺度或延伸范围
        '地质体形成时代',     # 描述形成的地质时代或时期
        '地质体成因类型',     # 描述形成机制或成因类别
        
        # === 新增：地球物理观测数据参数 (来自本体文件) ===
        '数据空间分辨率',     # 描述数据在空间上的分辨能力
        '数据采样间隔',       # 描述数据采样点之间的间距
        '数据噪声水平描述',   # 描述数据中噪声的整体情况
        '数据物理量类型',     # 描述反映的主要地球物理量类型
        '数据物性响应特征',   # 描述数据所体现的物性响应
        '数据维度结构',       # 描述一维、二维或三维结构
        '数据质量等级',       # 描述数据整体质量水平
        
        # === 新增：数据处理与反演算法指标 (来自本体文件) ===
        '算法参数数量',       # 描述算法涉及的主要参数数量
        '算法参数敏感性',     # 描述算法对参数变化的敏感程度
        '算法计算复杂度',     # 描述计算资源上的复杂程度
        '算法计算效率特征',   # 描述实际应用中的计算效率表现
        '算法适用场景'        # 描述适用的数据规模或场景
    ]
    entitys_labels_dict={# === 地震勘探与观测方法 ===
        '地震采集': 1,
        '三维地震勘探': 1,
        '四维地震勘探': 1,
        '深反射地震': 1,
        '深地震测深': 1,
        '井间地震剖面': 1,
        '多波地震勘探': 1,
        '反射波法': 1,
        '折射波法': 1,
        '面波勘探': 1,
        '微震监测': 1,
        '垂直地震剖面': 1, 
        '宽角反射': 1,
        '横波分裂测量': 1,
        '被动源地震勘探': 1,
        '节点地震采集': 1,
        '跨孔地震探测': 1,
        '震电勘探': 1,

        # === 地震仪器与设备系统 ===
        '地震探测仪器': 1,
        '地震传感器': 1,
        '三分量地震检波器': 1,
        'MEMS地震传感器': 1,
        '宽频带地震计': 1,
        '短周期地震计': 1,
        '长周期地震计': 1,
        '强震加速度计': 1,
        '井中地震仪': 1,
        '深井地震仪': 1,
        '海底地震仪': 1,
        '地震激发震源': 1,
        '可控震源': 1,
        '炸药震源': 1,
        '电火花震源': 1,
        '空气枪阵列': 1,
        '地震采集与记录系统': 1,
        '地震台阵与阵列系统': 1,
        '国家地震观测台网': 1,
        '区域地震观测台网': 1,
        '高密度地震采集系统': 1,
        '海洋多道地震采集系统': 1,

        # === 地震数据、处理与解释模型 ===
        '地震原始观测数据': 1,
        '地震地层单位': 1,
        '地震层序': 1,
        '反射波组': 1,
        '地震波速度模型': 1,
        '纵波速度模型': 1,
        '横波速度模型': 1,
        '波速比模型': 1,
        '地震属性分析': 1,
        '地震相分类': 1,
        '地震反演': 1,
        '全波形反演': 1,
        '层析成像': 1,
        'AVO反演': 1, # 对应 AVO/AVA反演
        '逆时偏移': 1,
        '克希霍夫偏移': 1,
        '动校正': 1,
        '静校正': 1,
        '初至自动拾取': 1 # 对应 初至/震相自动拾取
                }
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, default="example")
    parser.add_argument('--APIKEY', type=str, default="sk-7c36adfd428542d0b2400963c1da396c")
    parser.add_argument('--URL', type=str, default="https://dashscope.aliyuncs.com/compatible-mode/v1")    
    parser.add_argument('--model', type=str, default="qwen-plus")
    parser.add_argument('--embedding_model', type=str, default="BAAI/bge-m3")#默认是上面URL提供的
    parser.add_argument('--KGlink', type=str, default="bolt://localhost:7687")
    parser.add_argument('--KGname', type=str, default="neo4j")
    parser.add_argument('--KGcount', type=str, default="neo4j")
    parser.add_argument('--KGcode', type=str, default="neo4j@openspg")
    parser.add_argument('--KGentity_labels', type=dict, default=entitys_labels_dict)
    parser.add_argument('--KGfigure_labels', type=dict, default=figure_array)
    # 在原有的 APIKEY 和 URL 配置下面，增加这三行向量模型（SiliconFlow）的配置
    parser.add_argument('--EMBEDDING_APIKEY', type=str, default='sk-dlqrsvtdvflnqodxeknupmgzyjsxwrkcxohekevjnocltlwu')
    parser.add_argument('--EMBEDDING_URL', type=str, default='https://api.siliconflow.cn/v1')
    parser.add_argument('--EMBEDDING_MODEL', type=str, default='BAAI/bge-m3')
    args = parser.parse_args()

    # 可选：打印配置
    print(f"[CONFIG] APIKEY: {args.APIKEY}, URL: {args.URL}, MODEL: {args.model}")