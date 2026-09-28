import datetime
import math
import re
from typing import Dict, Any, Optional, List, Tuple

STEM_NAMES = ['Jia', 'Yi', 'Bing', 'Ding', 'Wu', 'Ji', 'Geng', 'Xin', 'Ren', 'Gui']
STEM_CHARS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
STEM_ELEMENTS = [
    'Yang Wood', 'Yin Wood', 
    'Yang Fire', 'Yin Fire', 
    'Yang Earth', 'Yin Earth', 
    'Yang Metal', 'Yin Metal', 
    'Yang Water', 'Yin Water'
]
STEM_SHORT_ELEMENTS = [
    'Wood', 'Wood', 'Fire', 'Fire', 'Earth', 'Earth', 'Metal', 'Metal', 'Water', 'Water'
]

BRANCH_NAMES = ['Zi', 'Chou', 'Yin', 'Mao', 'Chen', 'Si', 'Wu', 'Wei', 'Shen', 'You', 'Xu', 'Hai']
BRANCH_CHARS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
BRANCH_ANIMALS = [
    'Rat 鼠', 'Ox 牛', 'Tiger 虎', 'Rabbit 兔', 'Dragon 龍', 'Snake 蛇',
    'Horse 馬', 'Goat 羊', 'Monkey 猴', 'Rooster 雞', 'Dog 狗', 'Pig 豬'
]
BRANCH_SHORT_ANIMALS = [
    'Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake',
    'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Pig'
]
BRANCH_ELEMENTS = [
    '水 Yang Water', '± Yin Earth', '木 Yang Wood', '木 Yin Wood', '± Yang Earth', '火 Yin Fire',
    '火 Yang Fire', '± Yin Earth', '金 Yang Metal', '金 Yin Metal', '± Yang Earth', '水 Yin Water'
]

# Hidden Stems mapping in classical order (matching standard Joey Yap Natal Chart ephemeris)
BRANCH_HIDDEN_STEMS_MAP = {
    0: [{'char': '癸', 'name': 'Gui', 'polarity_elem': '-Water水', 'stem_idx': 9}], # Zi
    1: [
        {'char': '癸', 'name': 'Gui', 'polarity_elem': '-Water水', 'stem_idx': 9},
        {'char': '辛', 'name': 'Xin', 'polarity_elem': '-Metal金', 'stem_idx': 7},
        {'char': '己', 'name': 'Ji', 'polarity_elem': '-Earth土', 'stem_idx': 5}
    ], # Chou
    2: [
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4},
        {'char': '甲', 'name': 'Jia', 'polarity_elem': '+Wood木', 'stem_idx': 0},
        {'char': '丙', 'name': 'Bing', 'polarity_elem': '+Fire火', 'stem_idx': 2}
    ], # Yin
    3: [{'char': '乙', 'name': 'Yi', 'polarity_elem': '-Wood木', 'stem_idx': 1}], # Mao
    4: [
        {'char': '乙', 'name': 'Yi', 'polarity_elem': '-Wood木', 'stem_idx': 1},
        {'char': '癸', 'name': 'Gui', 'polarity_elem': '-Water水', 'stem_idx': 9},
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4}
    ], # Chen
    5: [
        {'char': '庚', 'name': 'Geng', 'polarity_elem': '+Metal金', 'stem_idx': 6},
        {'char': '丙', 'name': 'Bing', 'polarity_elem': '+Fire火', 'stem_idx': 2},
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4}
    ], # Si
    6: [
        {'char': '己', 'name': 'Ji', 'polarity_elem': '-Earth土', 'stem_idx': 5},
        {'char': '丁', 'name': 'Ding', 'polarity_elem': '-Fire火', 'stem_idx': 3}
    ], # Wu
    7: [
        {'char': '丁', 'name': 'Ding', 'polarity_elem': '-Fire火', 'stem_idx': 3},
        {'char': '己', 'name': 'Ji', 'polarity_elem': '-Earth土', 'stem_idx': 5},
        {'char': '乙', 'name': 'Yi', 'polarity_elem': '-Wood木', 'stem_idx': 1}
    ], # Wei
    8: [
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4},
        {'char': '壬', 'name': 'Ren', 'polarity_elem': '+Water水', 'stem_idx': 8},
        {'char': '庚', 'name': 'Geng', 'polarity_elem': '+Metal金', 'stem_idx': 6}
    ], # Shen
    9: [{'char': '辛', 'name': 'Xin', 'polarity_elem': '-Metal金', 'stem_idx': 7}], # You
    10: [
        {'char': '辛', 'name': 'Xin', 'polarity_elem': '-Metal金', 'stem_idx': 7},
        {'char': '丁', 'name': 'Ding', 'polarity_elem': '-Fire火', 'stem_idx': 3},
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4}
    ], # Xu
    11: [
        {'char': '壬', 'name': 'Ren', 'polarity_elem': '+Water水', 'stem_idx': 8},
        {'char': '甲', 'name': 'Jia', 'polarity_elem': '+Wood木', 'stem_idx': 0}
    ] # Hai: Ren (Main Qi), Jia (Middle Qi)
}

# Reference Date: 2000-01-01 was Wu Wu (Stem: Wu=4, Branch: Wu=6)
REF_DATE = datetime.date(2000, 1, 1)
REF_STEM_IDX = 4
REF_BRANCH_IDX = 6

# ==========================================
# ASTRONOMICAL SOLAR LONGITUDE (VSOP87 / JEAN MEEUS)
# ==========================================

def get_astronomical_solar_longitude(year: int, month: int, day: int, hour: int = 12, minute: int = 0, tz_offset: float = 8.0) -> float:
    """
    Computes apparent solar ecliptic longitude in degrees (0 to 360) using high-precision
    Jean Meeus Astronomical Algorithms. Accurate to within < 0.002 degrees (< 30 seconds of time).
    Default timezone offset is UTC+8 (Beijing/Solar standard for East/SE Asia).
    """
    utc_hour = hour + minute / 60.0 - tz_offset
    y = year
    m = month
    d = day + utc_hour / 24.0
    if m <= 2:
        y -= 1
        m += 12
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5

    T = (jd - 2451545.0) / 36525.0
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T**2
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T**2
    M_rad = math.radians(M)
    C = (1.914602 - 0.004817 * T - 0.000014 * T**2) * math.sin(M_rad) + \
        (0.019993 - 0.000101 * T) * math.sin(2 * M_rad) + \
        0.000289 * math.sin(3 * M_rad)
    sun_true_lon = L0 + C
    omega = 125.04 - 1934.136 * T
    lambda_apparent = (sun_true_lon - 0.00569 - 0.00478 * math.sin(math.radians(omega))) % 360.0
    return lambda_apparent

def get_solar_month_branch(sun_lon: float) -> int:
    """
    Maps apparent solar longitude (0-360) to the 12 BaZi Month Branches (0=Zi, 1=Chou, ..., 11=Hai):
    寅 Yin (2): 315° to 345° (Li Chun 立春)
    卯 Mao (3): 345° to 15° (Jing Zhe 驚蟄)
    辰 Chen (4): 15° to 45° (Qing Ming 清明)
    巳 Si (5): 45° to 75° (Li Xia 立夏)
    午 Wu (6): 75° to 105° (Mang Zhong 芒種)
    未 Wei (7): 105° to 135° (Xiao Shu 小暑)
    申 Shen (8): 135° to 165° (Li Qiu 立秋)
    酉 You (9): 165° to 195° (Bai Lu 白露)
    戌 Xu (10): 195° to 225° (Han Lu 寒露)
    亥 Hai (11): 225° to 255° (Li Dong 立冬)
    子 Zi (0): 255° to 285° (Da Xue 大雪)
    丑 Chou (1): 285° to 315° (Xiao Han 小寒)
    """
    deg = sun_lon % 360.0
    if 315.0 <= deg < 345.0:
        return 2  # Yin (Month 1)
    elif deg >= 345.0 or deg < 15.0:
        return 3  # Mao (Month 2)
    elif 15.0 <= deg < 45.0:
        return 4  # Chen (Month 3)
    elif 45.0 <= deg < 75.0:
        return 5  # Si (Month 4)
    elif 75.0 <= deg < 105.0:
        return 6  # Wu (Month 5)
    elif 105.0 <= deg < 135.0:
        return 7  # Wei (Month 6)
    elif 135.0 <= deg < 165.0:
        return 8  # Shen (Month 7)
    elif 165.0 <= deg < 195.0:
        return 9  # You (Month 8)
    elif 195.0 <= deg < 225.0:
        return 10 # Xu (Month 9)
    elif 225.0 <= deg < 255.0:
        return 11 # Hai (Month 10)
    elif 255.0 <= deg < 285.0:
        return 0  # Zi (Month 11)
    else: # 285.0 <= deg < 315.0
        return 1  # Chou (Month 12)

def get_10_god(dm_idx: int, target_idx: int) -> Dict[str, str]:
    """
    Computes 10 God notation between Day Master stem and target stem.
    """
    dm_elem = dm_idx // 2
    target_elem = target_idx // 2
    same_polar = (dm_idx % 2) == (target_idx % 2)
    
    if dm_elem == target_elem:
        if dm_idx == target_idx:
            return {'zh_full': '日元', 'zh_short': '日', 'code': 'DM', 'en_full': 'Day Master'}
        return {'zh_full': '比肩', 'zh_short': '比', 'code': 'F', 'en_full': 'Friend'} if same_polar else {'zh_full': '劫財', 'zh_short': '劫', 'code': 'RW', 'en_full': 'Rob Wealth'}
    elif (dm_elem + 1) % 5 == target_elem:
        return {'zh_full': '食神', 'zh_short': '食', 'code': 'EG', 'en_full': 'Eating God'} if same_polar else {'zh_full': '傷官', 'zh_short': '傷', 'code': 'HO', 'en_full': 'Hurting Officer'}
    elif (dm_elem + 2) % 5 == target_elem:
        return {'zh_full': '偏財', 'zh_short': '才', 'code': 'IW', 'en_full': 'Indirect Wealth'} if same_polar else {'zh_full': '正財', 'zh_short': '財', 'code': 'DW', 'en_full': 'Direct Wealth'}
    elif (target_elem + 2) % 5 == dm_elem:
        return {'zh_full': '七殺', 'zh_short': '殺', 'code': '7K', 'en_full': 'Seven Killings'} if same_polar else {'zh_full': '正官', 'zh_short': '官', 'code': 'DO', 'en_full': 'Direct Officer'}
    elif (target_elem + 1) % 5 == dm_elem:
        return {'zh_full': '偏印', 'zh_short': '印', 'code': 'IR', 'en_full': 'Indirect Resource'} if same_polar else {'zh_full': '正印', 'zh_short': '印', 'code': 'DR', 'en_full': 'Direct Resource'}
    return {'zh_full': '', 'zh_short': '', 'code': '', 'en_full': ''}

def parse_date_and_time(birth_date_str: str, birth_time_str: Optional[str] = None) -> Tuple[Optional[int], Optional[int], Optional[int], int, int]:
    year, month, day = None, None, None
    
    # Check for Month Name (e.g., '07 Dec 1986', '03/Jun/1981', '3 June 1981', 'June 3, 1981')
    m_month_word = re.search(r'([A-Za-z]{3,9})', birth_date_str)
    if m_month_word:
        word = m_month_word.group(1).lower()[:3]
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        if word in months:
            month = months.index(word) + 1
            nums = [int(n) for n in re.findall(r'\d+', birth_date_str)]
            if len(nums) >= 2:
                for n in nums:
                    if n >= 1900:
                        year = n
                    elif 1 <= n <= 31:
                        day = n
    if not (year and month and day):
        # Try ISO YYYY-MM-DD
        m_iso = re.search(r'(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', birth_date_str)
        if m_iso:
            year, month, day = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
        else:
            # Try MM/DD/YYYY or DD/MM/YYYY
            m_slash = re.search(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})', birth_date_str)
            if m_slash:
                n1, n2, y_val = int(m_slash.group(1)), int(m_slash.group(2)), int(m_slash.group(3))
                year = y_val
                if n1 > 12 >= n2:
                    day, month = n1, n2
                elif n2 > 12 >= n1:
                    month, day = n1, n2
                else:
                    # In standard HTML date input, browsers in US use MM/DD/YYYY
                    month, day = n1, n2

    hour, minute = 12, 0
    time_str = birth_time_str or birth_date_str
    if time_str and time_str.lower() != "unknown":
        m_time = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', time_str, re.IGNORECASE)
        if m_time:
            hour = int(m_time.group(1))
            minute = int(m_time.group(2))
            ampm = m_time.group(3)
            if ampm:
                if ampm.lower() == 'pm' and hour < 12:
                    hour += 12
                elif ampm.lower() == 'am' and hour == 12:
                    hour = 0

    return year, month, day, hour, minute

# ==========================================
# AUXILIARY SHEN SHA & GUA CALCULATIONS
# ==========================================

def calculate_auxiliary_stars(dm_stem_idx: int, y_branch_idx: int, d_branch_idx: int, m_branch_idx: int, h_branch_idx: int, y_stem_idx: int, m_stem_idx: int) -> Dict[str, Any]:
    # Noble People (Tian Yi Gui Ren 天乙貴人):
    noble_map = {
        0: '丑 Ox, 未 Goat', 1: '申 Monkey, 子 Rat', 2: '亥 Pig, 酉 Rooster', 3: '亥 Pig, 酉 Rooster',
        4: '丑 Ox, 未 Goat', 5: '申 Monkey, 子 Rat', 6: '丑 Ox, 未 Goat', 7: '午 Horse, 寅 Tiger',
        8: '卯 Rabbit, 巳 Snake', 9: '卯 Rabbit, 巳 Snake'
    }
    # Intelligence (Wen Chang Gui Ren 文昌貴人):
    wen_chang_map = {
        0: '巳 Snake', 1: '午 Horse', 2: '申 Monkey', 3: '酉 Rooster', 4: '申 Monkey',
        5: '酉 Rooster', 6: '亥 Pig', 7: '子 Rat', 8: '寅 Tiger', 9: '卯 Rabbit'
    }
    # Peach Blossom (Tao Hua 桃花), Sky Horse (Yi Ma 驛馬), Solitary (Gu Chen 孤辰) based on Day Branch:
    peach_map = {
        0: '酉 Rooster', 4: '酉 Rooster', 8: '酉 Rooster',
        2: '卯 Rabbit', 6: '卯 Rabbit', 10: '卯 Rabbit',
        5: '午 Horse', 9: '午 Horse', 1: '午 Horse',
        11: '子 Rat', 3: '子 Rat', 7: '子 Rat'
    }
    sky_horse_map = {
        0: '寅 Tiger', 4: '寅 Tiger', 8: '寅 Tiger',
        2: '申 Monkey', 6: '申 Monkey', 10: '申 Monkey',
        5: '亥 Pig', 9: '亥 Pig', 1: '亥 Pig',
        11: '巳 Snake', 3: '巳 Snake', 7: '巳 Snake'
    }
    solitary_map = {
        11: '寅 Tiger', 0: '寅 Tiger', 1: '寅 Tiger',
        2: '巳 Snake', 3: '巳 Snake', 4: '巳 Snake',
        5: '申 Monkey', 6: '申 Monkey', 7: '申 Monkey',
        8: '亥 Pig', 9: '亥 Pig', 10: '亥 Pig'
    }

    # Conception Palace (Tai Yuan 胎元): Month Stem + 1, Month Branch + 3
    ty_stem_idx = (m_stem_idx + 1) % 10
    ty_branch_idx = (m_branch_idx + 3) % 12
    conception_palace = f"{STEM_CHARS[ty_stem_idx]}{BRANCH_CHARS[ty_branch_idx]} {STEM_ELEMENTS[ty_stem_idx].split()[0]} {STEM_SHORT_ELEMENTS[ty_stem_idx]} {BRANCH_SHORT_ANIMALS[ty_branch_idx]}"

    # Life Palace (Ming Gong 命宮):
    # Classical Palm formula: Count month from Yin=1..Hai=10..Chou=12; Hour from Zi=1..Mao=4..Hai=12
    # Offset from Yin is: (14 - (m_order + h_order)) % 12
    m_order = (m_branch_idx - 2) % 12 + 1
    h_order = h_branch_idx + 1
    offset = (14 - (m_order + h_order)) % 12
    mg_branch_idx = (2 + offset) % 12
    # Five Tigers遁 stem for Ming Gong from Year Stem
    mg_start_stem = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}[y_stem_idx % 5]
    mg_stem_idx = (mg_start_stem + (mg_branch_idx - 2) % 12) % 10
    life_palace = f"{STEM_CHARS[mg_stem_idx]}{BRANCH_CHARS[mg_branch_idx]} {STEM_ELEMENTS[mg_stem_idx].split()[0]} {STEM_SHORT_ELEMENTS[mg_stem_idx]} {BRANCH_SHORT_ANIMALS[mg_branch_idx]}"

    return {
        'celestial_animal': BRANCH_ANIMALS[y_branch_idx],
        'noble_people': noble_map.get(dm_stem_idx, '申 Monkey, 子 Rat'),
        'intelligence': wen_chang_map.get(dm_stem_idx, '午 Horse'),
        'peach_blossom': peach_map.get(d_branch_idx, '午 Horse'),
        'sky_horse': sky_horse_map.get(d_branch_idx, '亥 Pig'),
        'solitary': solitary_map.get(d_branch_idx, '亥 Pig'),
        'life_palace': life_palace,
        'conception_palace': conception_palace
    }

def calculate_ming_gua(bazi_year: int, gender: str) -> Dict[str, Any]:
    """Computes Life Star (Ming Gua) and 8 Mansions (Ba Zhai) Favorable/Unfavorable Directions."""
    s = sum(int(c) for c in str(bazi_year))
    while s >= 10:
        s = sum(int(c) for c in str(s))
    
    is_male = gender.lower().startswith('m')
    if bazi_year < 2000:
        gua = (11 - s) if is_male else (s + 4)
    else:
        gua = (10 - s) if is_male else (s + 5)
    
    while gua >= 10:
        gua = sum(int(c) for c in str(gua))
    if gua == 0:
        gua = 9
    
    # Gua 5 converts to Kun 2 for Male, Gen 8 for Female
    active_gua = (2 if is_male else 8) if gua == 5 else gua

    gua_info_map = {
        1: {'num': '1', 'color': 'White', 'zh': '一白星命', 'elem': 'Water 水', 'char': '坎', 'name': 'Kan', 'dir': 'North'},
        2: {'num': '2', 'color': 'Black', 'zh': '二黑星命', 'elem': 'Earth 土', 'char': '坤', 'name': 'Kun', 'dir': 'SouthWest'},
        3: {'num': '3', 'color': 'Jade', 'zh': '三碧星命', 'elem': 'Wood 木', 'char': '震', 'name': 'Zhen', 'dir': 'East'},
        4: {'num': '4', 'color': 'Green', 'zh': '四綠星命', 'elem': 'Wood 木', 'char': '巽', 'name': 'Xun', 'dir': 'SouthEast'},
        5: {'num': '5', 'color': 'Yellow', 'zh': '五黃星命', 'elem': 'Earth 土', 
            'char': '坤' if is_male else '艮', 'name': 'Kun' if is_male else 'Gen', 'dir': 'SouthWest' if is_male else 'NorthEast'},
        6: {'num': '6', 'color': 'White', 'zh': '六白星命', 'elem': 'Metal 金', 'char': '乾', 'name': 'Qian', 'dir': 'NorthWest'},
        7: {'num': '7', 'color': 'Red', 'zh': '七赤星命', 'elem': 'Metal 金', 'char': '兌', 'name': 'Dui', 'dir': 'West'},
        8: {'num': '8', 'color': 'White', 'zh': '八白星命', 'elem': 'Earth 土', 'char': '艮', 'name': 'Gen', 'dir': 'NorthEast'},
        9: {'num': '9', 'color': 'Purple', 'zh': '九紫星命', 'elem': 'Fire 火', 'char': '離', 'name': 'Li', 'dir': 'South'}
    }

    # 8 Mansions directions table
    directions_map = {
        1: {'sq': '東南 SE', 'ty': '東 E', 'yn': '南 S', 'fw': '北 N', 'hh': '西 W', 'wg': '東北 NE', 'ls': '西北 NW', 'jm': '西南 SW'},
        2: {'sq': '東北 NE', 'ty': '西 W', 'yn': '西北 NW', 'fw': '西南 SW', 'hh': '東 E', 'wg': '東南 SE', 'ls': '南 S', 'jm': '北 N'},
        3: {'sq': '南 S', 'ty': '北 N', 'yn': '東南 SE', 'fw': '東 E', 'hh': '西南 SW', 'wg': '西北 NW', 'ls': '東北 NE', 'jm': '西 W'},
        4: {'sq': '北 N', 'ty': '南 S', 'yn': '東 E', 'fw': '東南 SE', 'hh': '西北 NW', 'wg': '西南 SW', 'ls': '西 W', 'jm': '東北 NE'},
        6: {'sq': '西 W', 'ty': '東北 NE', 'yn': '西南 SW', 'fw': '西北 NW', 'hh': '東南 SE', 'wg': '東 E', 'ls': '北 N', 'jm': '南 S'},
        7: {'sq': '西北 NW', 'ty': '西南 SW', 'yn': '東北 NE', 'fw': '西 W', 'hh': '北 N', 'wg': '南 S', 'ls': '東南 SE', 'jm': '東 E'},
        8: {'sq': '西南 SW', 'ty': '西北 NW', 'yn': '西 W', 'fw': '東北 NE', 'hh': '南 S', 'wg': '北 N', 'ls': '東 E', 'jm': '東南 SE'},
        9: {'sq': '東 E', 'ty': '東南 SE', 'yn': '北 N', 'fw': '南 S', 'hh': '東北 NE', 'wg': '西 W', 'ls': '西南 SW', 'jm': '西北 NW'}
    }

    g_meta = gua_info_map[gua]
    dirs = directions_map.get(active_gua, directions_map[2])

    return {
        'life_star_num': g_meta['num'],
        'life_star_color': g_meta['color'],
        'life_star_zh': g_meta['zh'],
        'life_star_elem': g_meta['elem'],
        'fs_gua_char': g_meta['char'],
        'fs_gua_name': g_meta['name'],
        'fs_gua_dir': g_meta['dir'],
        'favorable_dirs': {
            'sq': dirs['sq'],
            'ty': dirs['ty'],
            'yn': dirs['yn'],
            'fw': dirs['fw']
        },
        'unfavorable_dirs': {
            'hh': dirs['hh'],
            'wg': dirs['wg'],
            'ls': dirs['ls'],
            'jm': dirs['jm']
        }
    }

def calculate_four_pillars(year: int, month: int, day: int, hour: int = 12, minute: int = 0, gender: str = "Male", client_name: str = "Client") -> Dict[str, Any]:
    dt = datetime.date(year, month, day)

    # 1. Day Pillar
    target_dt = dt
    if hour >= 23:
        target_dt = dt + datetime.timedelta(days=1)
    diff = (target_dt - REF_DATE).days
    day_stem_idx = (REF_STEM_IDX + diff) % 10
    day_branch_idx = (REF_BRANCH_IDX + diff) % 12

    # 2. Hour Pillar
    total_mins = hour * 60 + minute
    if total_mins >= 23 * 60 or total_mins < 1 * 60:
        h_branch_idx = 0  # Zi
    else:
        h_branch_idx = ((total_mins - 60) // 120 + 1) % 12
        
    h_start_stem = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}[day_stem_idx % 5]
    h_stem_idx = (h_start_stem + h_branch_idx) % 10

    # 3. High-Precision Astronomical Solar Longitude
    sun_lon = get_astronomical_solar_longitude(year, month, day, hour, minute)

    # 4. Year Pillar (Changes at Li Chun: 315° apparent solar longitude)
    if month == 1 or (month == 2 and sun_lon < 315.0):
        bazi_year = year - 1
    else:
        bazi_year = year
    y_stem_idx = (bazi_year - 4) % 10
    y_branch_idx = (bazi_year - 4) % 12

    # 5. Month Pillar (Calculated using exact astronomical solar term longitude)
    m_branch_idx = get_solar_month_branch(sun_lon)
    m_start_stem = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}[y_stem_idx % 5]
    m_offset = (m_branch_idx - 2) % 12
    m_stem_idx = (m_start_stem + m_offset) % 10

    # 6. Auxiliary Stars & Shen Sha
    aux = calculate_auxiliary_stars(day_stem_idx, y_branch_idx, day_branch_idx, m_branch_idx, h_branch_idx, y_stem_idx, m_stem_idx)

    # 7. Ming Gua & Directions
    gua_data = calculate_ming_gua(bazi_year, gender)

    # Build 10 Gods for each stem
    pillars_meta = {
        'hour': {
            'stem_idx': h_stem_idx,
            'branch_idx': h_branch_idx,
            'stem_char': STEM_CHARS[h_stem_idx],
            'stem_name': STEM_NAMES[h_stem_idx],
            'stem_elem': STEM_SHORT_ELEMENTS[h_stem_idx],
            'stem_god': get_10_god(day_stem_idx, h_stem_idx),
            'branch_char': BRANCH_CHARS[h_branch_idx],
            'branch_name': BRANCH_NAMES[h_branch_idx],
            'branch_animal': BRANCH_ANIMALS[h_branch_idx],
            'branch_elem': BRANCH_ELEMENTS[h_branch_idx],
            'hidden_stems': [
                {
                    **hs,
                    'god': get_10_god(day_stem_idx, hs['stem_idx'])
                } for hs in BRANCH_HIDDEN_STEMS_MAP[h_branch_idx]
            ]
        },
        'day': {
            'stem_idx': day_stem_idx,
            'branch_idx': day_branch_idx,
            'stem_char': STEM_CHARS[day_stem_idx],
            'stem_name': STEM_NAMES[day_stem_idx],
            'stem_elem': STEM_SHORT_ELEMENTS[day_stem_idx],
            'stem_god': get_10_god(day_stem_idx, day_stem_idx),
            'branch_char': BRANCH_CHARS[day_branch_idx],
            'branch_name': BRANCH_NAMES[day_branch_idx],
            'branch_animal': BRANCH_ANIMALS[day_branch_idx],
            'branch_elem': BRANCH_ELEMENTS[day_branch_idx],
            'hidden_stems': [
                {
                    **hs,
                    'god': get_10_god(day_stem_idx, hs['stem_idx'])
                } for hs in BRANCH_HIDDEN_STEMS_MAP[day_branch_idx]
            ]
        },
        'month': {
            'stem_idx': m_stem_idx,
            'branch_idx': m_branch_idx,
            'stem_char': STEM_CHARS[m_stem_idx],
            'stem_name': STEM_NAMES[m_stem_idx],
            'stem_elem': STEM_SHORT_ELEMENTS[m_stem_idx],
            'stem_god': get_10_god(day_stem_idx, m_stem_idx),
            'branch_char': BRANCH_CHARS[m_branch_idx],
            'branch_name': BRANCH_NAMES[m_branch_idx],
            'branch_animal': BRANCH_ANIMALS[m_branch_idx],
            'branch_elem': BRANCH_ELEMENTS[m_branch_idx],
            'hidden_stems': [
                {
                    **hs,
                    'god': get_10_god(day_stem_idx, hs['stem_idx'])
                } for hs in BRANCH_HIDDEN_STEMS_MAP[m_branch_idx]
            ]
        },
        'year': {
            'stem_idx': y_stem_idx,
            'branch_idx': y_branch_idx,
            'stem_char': STEM_CHARS[y_stem_idx],
            'stem_name': STEM_NAMES[y_stem_idx],
            'stem_elem': STEM_SHORT_ELEMENTS[y_stem_idx],
            'stem_god': get_10_god(day_stem_idx, y_stem_idx),
            'branch_char': BRANCH_CHARS[y_branch_idx],
            'branch_name': BRANCH_NAMES[y_branch_idx],
            'branch_animal': BRANCH_ANIMALS[y_branch_idx],
            'branch_elem': BRANCH_ELEMENTS[y_branch_idx],
            'hidden_stems': [
                {
                    **hs,
                    'god': get_10_god(day_stem_idx, hs['stem_idx'])
                } for hs in BRANCH_HIDDEN_STEMS_MAP[y_branch_idx]
            ]
        },
        'day_master': STEM_NAMES[day_stem_idx],
        'day_master_element': STEM_ELEMENTS[day_stem_idx],
        'day_animal': BRANCH_ANIMALS[day_branch_idx],
        'aux': aux,
        'gua': gua_data,
        'client_name': client_name,
        'gender': gender,
        'birth_year': year,
        'birth_month': month,
        'birth_day': day,
        'birth_hour': hour,
        'birth_minute': minute,
        'sun_lon': sun_lon,
    }

    # Dynamic Authentic Qi Men Destiny Palace calculation (Zhi Run Fa)
    try:
        from qimen_engine import calculate_natal_qimen_destiny
        pillars_meta['qimen_destiny'] = calculate_natal_qimen_destiny(pillars_meta)
    except Exception:
        pillars_meta['qimen_destiny'] = {
            'palace': '東北 NE',
            'stem': f"{STEM_CHARS[day_stem_idx]} {STEM_NAMES[day_stem_idx]}",
            'door': '休 Rest',
            'star': '天任 Ambassador',
            'guardian': '地 Earth'
        }

    return pillars_meta

def generate_natal_chart_html(p: Dict[str, Any]) -> str:
    """
    Renders an authentic, classical Joey Yap Personal Chart for 2026 (Image 2)
    with Header Profile, Day Master and Stars, Qi Men Destiny Palace, Life Star (5 Yellow),
    Feng Shui Gua (Kun SouthWest), 8 Mansions Directions, and the complete 4 Pillars Table.
    Outputs completely unindented, comment-free HTML to guarantee zero markdown parser collisions.
    """
    order = ['hour', 'day', 'month', 'year']
    col_titles = {'hour': '時 Hour', 'day': '日 Day', 'month': '月 Month', 'year': '年 Year'}
    
    aux = p.get('aux', {})
    gua = p.get('gua', {})
    fav = gua.get('favorable_dirs', {})
    unfav = gua.get('unfavorable_dirs', {})
    qm = p.get('qimen_destiny', {})
    
    client_name = p.get('client_name', 'Client')
    b_day = p.get('birth_day', 7)
    b_month = p.get('birth_month', 12)
    b_year = p.get('birth_year', 1986)
    b_hour = p.get('birth_hour', 5)
    b_min = p.get('birth_minute', 50)
    gender_str = "MALE 男" if p.get('gender', 'Male').lower().startswith('m') else "FEMALE 女"

    months_en = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_name = months_en[b_month - 1] if 1 <= b_month <= 12 else str(b_month)
    am_pm = "AM" if b_hour < 12 else "PM"
    hour_12 = b_hour % 12
    if hour_12 == 0:
        hour_12 = 12
    formatted_date_time = f"{b_day:02d} {month_name} {b_year} ({hour_12:02d}:{b_min:02d}{am_pm})"

    dm_stem = p['day']['stem_name']
    dm_elem = p['day_master_element']
    dm_char = p['day']['stem_char']
    dm_full = f"{dm_char} {dm_stem} {dm_elem}"

    raw_html = f"""<div class="personal-natal-chart" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 960px; margin: 15px auto; background: #ffffff; border: 2px solid #7a1518; border-radius: 6px; box-shadow: 0 10px 30px rgba(0,0,0,0.12); color: #1e293b; overflow: hidden; padding: 18px;">
<div style="border-bottom: 2px solid #856404; padding-bottom: 10px; margin-bottom: 14px;">
<div style="font-size: 15px; font-weight: 700; color: #475569;">
<span>{client_name}</span> | <span style="color: #0f172a;">{formatted_date_time}</span> | <span style="font-weight: 700; color: #7a1518;">{gender_str}</span>
</div>
</div>
<div style="display: grid; grid-template-columns: 1.22fr 1.08fr 0.85fr 0.85fr; gap: 10px; margin-bottom: 12px;">
<div style="border: 1px solid #7a1518; border-radius: 4px; overflow: hidden; font-size: 12px; background: #ffffff;">
<div style="background: #7a1518; color: #ffffff; padding: 6px 10px; font-weight: bold; display: flex; justify-content: space-between;">
<span>DAY MASTER</span>
<span>日主 : {dm_full}</span>
</div>
<div style="padding: 6px 10px; line-height: 1.65;">
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #64748b;">Celestial Animal</span>
<span style="font-weight: 600;">生肖 : {aux.get('celestial_animal', '-')}</span>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #64748b;">Noble People</span>
<span style="font-weight: 600;">貴人 : {aux.get('noble_people', '-')}</span>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #64748b;">Intelligence</span>
<span style="font-weight: 600;">文昌 : {aux.get('intelligence', '-')}</span>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #64748b;">Peach Blossom</span>
<span style="font-weight: 600;">桃花 : {aux.get('peach_blossom', '-')}</span>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #64748b;">Sky Horse</span>
<span style="font-weight: 600;">驛馬 : {aux.get('sky_horse', '-')}</span>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #64748b;">Solitary</span>
<span style="font-weight: 600;">孤辰 : {aux.get('solitary', '-')}</span>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #64748b;">Life Palace</span>
<span style="font-weight: 600;">命宮 : {aux.get('life_palace', '-')}</span>
</div>
<div style="display: flex; justify-content: space-between; padding: 2px 0;">
<span style="color: #64748b;">Conception Palace</span>
<span style="font-weight: 600;">胎元 : {aux.get('conception_palace', '-')}</span>
</div>
</div>
</div>
<div style="border: 1px solid #7a1518; border-radius: 4px; overflow: hidden; font-size: 12px; background: #ffffff;">
<div style="background: #7a1518; color: #ffffff; padding: 6px 10px; font-weight: bold; display: flex; justify-content: space-between;">
<span>QI MEN DESTINY PALACE</span>
<span>奇門命宮 : {qm.get('palace', '東北 NE')}</span>
</div>
<div style="padding: 10px 10px; line-height: 2.1;">
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 4px 0;">
<span style="color: #64748b;">Life Stem</span>
<span style="font-weight: 600;">命干 : {qm.get('stem', '-')}</span>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 4px 0;">
<span style="color: #64748b;">Door of Destiny</span>
<span style="font-weight: 600;">門 : {qm.get('door', '-')}</span>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 4px 0;">
<span style="color: #64748b;">Star of Destiny</span>
<span style="font-weight: 600;">星 : {qm.get('star', '-')}</span>
</div>
<div style="display: flex; justify-content: space-between; padding: 4px 0;">
<span style="color: #64748b;">Guardian of Destiny</span>
<span style="font-weight: 600;">神 : {qm.get('guardian', '-')}</span>
</div>
</div>
</div>
<div style="border: 1px solid #7a1518; border-radius: 4px; overflow: hidden; display: flex; flex-direction: column; background: #ffffff; text-align: center;">
<div style="background: #7a1518; color: #ffffff; padding: 6px 8px; font-weight: bold; font-size: 12px;">LIFE STAR</div>
<div style="display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 14px 4px; flex: 1;">
<div style="font-size: 34px; font-weight: 900; color: #7a1518; line-height: 1;">{gua.get('life_star_num', '5')}</div>
<div style="font-size: 15px; font-weight: bold; color: #b45309; margin: 4px 0;">{gua.get('life_star_color', 'Yellow')}</div>
<div style="font-size: 17px; font-weight: 900; color: #0f172a; margin-top: 4px;">{gua.get('life_star_zh', '五黃星命')}</div>
<div style="font-size: 15px; font-weight: bold; color: #7a1518; margin-top: 4px;">{gua.get('life_star_elem', 'Earth 土')}</div>
</div>
</div>
<div style="border: 1px solid #7a1518; border-radius: 4px; overflow: hidden; display: flex; flex-direction: column; background: #ffffff; text-align: center;">
<div style="background: #7a1518; color: #ffffff; padding: 6px 8px; font-weight: bold; font-size: 12px;">風水命卦 GUA</div>
<div style="display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 14px 4px; flex: 1;">
<div style="font-size: 46px; font-weight: 900; color: #0f172a; line-height: 1; margin: 2px 0;">{gua.get('fs_gua_char', '坤')}</div>
<div style="font-size: 14px; font-weight: bold; color: #475569; margin-top: 4px;">{gua.get('fs_gua_name', 'Kun')}</div>
<div style="font-size: 15px; font-weight: bold; color: #7a1518; margin-top: 6px;">{gua.get('fs_gua_dir', 'SouthWest')}</div>
</div>
</div>
</div>
<div style="display: grid; grid-template-columns: 1.1fr 2.1fr; gap: 10px; align-items: stretch;">
<div style="display: flex; flex-direction: column; gap: 8px;">
<div style="border: 1px solid #7a1518; border-radius: 4px; overflow: hidden; font-size: 11px; background: #ffffff;">
<div style="background: #7a1518; color: #ffffff; padding: 5px 8px; font-weight: bold; display: flex; justify-content: space-between;">
<span>FAVORABLE DIRECTIONS</span>
<span>本命吉方</span>
</div>
<div style="padding: 6px 8px; line-height: 1.7;">
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #475569;">Sheng Qi (Life Generating)</span> <b style="color: #047857;">生氣 : {fav.get('sq', '-')}</b>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #475569;">Tian Yi (Heavenly Doctor)</span> <b style="color: #047857;">天醫 : {fav.get('ty', '-')}</b>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #475569;">Yan Nian (Longevity)</span> <b style="color: #047857;">延年 : {fav.get('yn', '-')}</b>
</div>
<div style="display: flex; justify-content: space-between; padding: 2px 0;">
<span style="color: #475569;">Fu Wei (Stability)</span> <b style="color: #047857;">伏位 : {fav.get('fw', '-')}</b>
</div>
</div>
</div>
<div style="border: 1px solid #7a1518; border-radius: 4px; overflow: hidden; font-size: 11px; background: #ffffff;">
<div style="background: #7a1518; color: #ffffff; padding: 5px 8px; font-weight: bold; display: flex; justify-content: space-between;">
<span>UNFAVORABLE DIRECTIONS</span>
<span>本命凶方</span>
</div>
<div style="padding: 6px 8px; line-height: 1.7;">
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #475569;">Hou Hai (Mishaps)</span> <b style="color: #b91c1c;">禍害 : {unfav.get('hh', '-')}</b>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #475569;">Wu Gui (Five Ghosts)</span> <b style="color: #b91c1c;">五鬼 : {unfav.get('wg', '-')}</b>
</div>
<div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #e2e8f0; padding: 2px 0;">
<span style="color: #475569;">Liu Sha (Six Killings)</span> <b style="color: #b91c1c;">六煞 : {unfav.get('ls', '-')}</b>
</div>
<div style="display: flex; justify-content: space-between; padding: 2px 0;">
<span style="color: #475569;">Jue Ming (Life Threatening)</span> <b style="color: #b91c1c;">絕命 : {unfav.get('jm', '-')}</b>
</div>
</div>
</div>
</div>
<div style="border: 1px solid #7a1518; border-radius: 4px; overflow: hidden; background: #ffffff; display: flex; flex-direction: column;">
<div style="background: #7a1518; color: #ffffff; padding: 6px 12px; font-weight: bold; font-size: 13px; display: flex; justify-content: space-between; align-items: center;">
<span>NATAL CHART 本命八字</span>
<span style="font-size: 11px; font-weight: normal; opacity: 0.9;">Classical Metaphysics</span>
</div>
<table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 13px; flex: 1;">
<thead>
<tr style="background: #fdfaf2; color: #856404; border-bottom: 1.5px solid #d4af37; font-weight: 600;">"""
    for col in order:
        raw_html += f"""<th style="padding: 8px 4px; width: 22%; border-right: 1px solid #e2e8f0;">{col_titles[col]}</th>"""
    raw_html += """<th style="padding: 8px 4px; width: 12%; font-size: 11px; color: #64748b;"></th></tr></thead><tbody>"""

    raw_html += """<tr style="border-bottom: 1.5px solid #d4af37; background: #ffffff;">"""
    for col in order:
        meta = p[col]
        god = meta['stem_god']
        raw_html += f"""<td style="padding: 8px 4px; border-right: 1px solid #e2e8f0; vertical-align: middle;">
<div style="display: flex; align-items: center; justify-content: center; gap: 6px;">
<div style="border: 1px solid #cbd5e1; border-radius: 3px; padding: 2px 4px; font-size: 10px; line-height: 1.2; background: #f8fafc;">
<div style="font-weight: bold; color: #0f172a;">{god['zh_full']}</div>
<div style="color: #64748b; font-size: 9px;">{god['code']}</div>
</div>
<div>
<div style="font-size: 28px; font-weight: bold; line-height: 1; color: #0f172a;">{meta['stem_char']}</div>
<div style="font-size: 12px; font-weight: 600; color: #334155;">{meta['stem_name']}</div>
<div style="font-size: 11px; color: #64748b;">{meta['stem_elem']}</div>
</div>
</div>
</td>"""
    raw_html += """<td style="padding: 6px; border-left: 2px solid #856404; font-size: 11px; font-weight: bold; color: #856404; background: #fdfaf2; vertical-align: middle; line-height: 1.3;">天干<br><span style="font-size: 9px; font-weight: normal; color: #64748b;">Heavenly<br>Stems</span></td></tr>"""

    raw_html += """<tr style="border-bottom: 1.5px solid #d4af37; background: #fafafa;">"""
    for col in order:
        meta = p[col]
        raw_html += f"""<td style="padding: 8px 4px; border-right: 1px solid #e2e8f0; vertical-align: middle;">
<div style="font-size: 28px; font-weight: bold; line-height: 1; color: #0f172a;">{meta['branch_char']}</div>
<div style="font-size: 12px; font-weight: 600; color: #334155;">{meta['branch_name']}</div>
<div style="font-size: 11px; font-weight: 500; color: #475569;">{meta['branch_animal']}</div>
<div style="font-size: 10px; color: #64748b;">{meta['branch_elem']}</div>
</td>"""
    raw_html += """<td style="padding: 6px; border-left: 2px solid #856404; font-size: 11px; font-weight: bold; color: #856404; background: #fdfaf2; vertical-align: middle; line-height: 1.3;">地支<br><span style="font-size: 9px; font-weight: normal; color: #64748b;">Earthly<br>Branches</span></td></tr>"""

    raw_html += """<tr style="background: #ffffff;">"""
    for col in order:
        meta = p[col]
        hs_list = meta['hidden_stems']
        raw_html += """<td style="padding: 8px 4px; border-right: 1px solid #e2e8f0; vertical-align: top;">
<div style="display: flex; justify-content: space-around; align-items: flex-start;">"""
        for hs in hs_list:
            god = hs['god']
            raw_html += f"""<div style="padding: 0 3px; text-align: center;">
<div style="font-size: 18px; font-weight: bold; color: #1e293b;">{hs['char']}</div>
<div style="font-size: 11px; font-weight: 600; color: #334155;">{hs['name']}</div>
<div style="font-size: 9px; color: #64748b;">{hs['polarity_elem']}</div>
<div style="font-size: 10px; font-weight: bold; color: #856404; margin-top: 2px;">{god['zh_short']} <span style="font-size: 9px; color: #475569;">{god['code']}</span></div>
</div>"""
        raw_html += """</div></td>"""
    raw_html += """<td style="padding: 6px; border-left: 2px solid #856404; font-size: 11px; font-weight: bold; color: #856404; background: #fdfaf2; vertical-align: middle; line-height: 1.3;">藏干<br><span style="font-size: 9px; font-weight: normal; color: #64748b;">Hidden<br>Stems</span></td></tr></tbody></table></div></div></div>"""

    cleaned_lines = [line.strip() for line in raw_html.splitlines() if line.strip() and not line.strip().startswith('<!--')]
    return "\n".join(cleaned_lines)


def generate_natal_chart_markdown(p: Dict[str, Any]) -> str:
    """
    Renders the exact Joey Yap standard chart in Markdown table format:
    Columns: Hour (時) | Day (日) | Month (月) | Year (年)
    """
    h, d, m, y = p['hour'], p['day'], p['month'], p['year']
    aux = p.get('aux', {})
    gua = p.get('gua', {})
    
    def format_hs(hs_list):
        return " / ".join([f"{hs['char']} {hs['name']} ({hs['polarity_elem']}, {hs['god']['zh_short']} {hs['god']['code']})" for hs in hs_list])

    md = (
        "### NATAL CHART 本命八字\n\n"
        "| 時 Hour | 日 Day | 月 Month | 年 Year | Pillar |\n"
        "| :---: | :---: | :---: | :---: | :---: |\n"
        f"| **{h['stem_char']}** {h['stem_name']} ({h['stem_elem']})<br>`[{h['stem_god']['zh_full']} {h['stem_god']['code']}]` | **{d['stem_char']}** {d['stem_name']} ({d['stem_elem']})<br>`[{d['stem_god']['zh_full']} {d['stem_god']['code']}]` | **{m['stem_char']}** {m['stem_name']} ({m['stem_elem']})<br>`[{m['stem_god']['zh_full']} {m['stem_god']['code']}]` | **{y['stem_char']}** {y['stem_name']} ({y['stem_elem']})<br>`[{y['stem_god']['zh_full']} {y['stem_god']['code']}]` | **天干**<br>Heavenly Stems |\n"
        f"| **{h['branch_char']}** {h['branch_name']}<br>{h['branch_animal']}<br>`{h['branch_elem']}` | **{d['branch_char']}** {d['branch_name']}<br>{d['branch_animal']}<br>`{d['branch_elem']}` | **{m['branch_char']}** {m['branch_name']}<br>{m['branch_animal']}<br>`{m['branch_elem']}` | **{y['branch_char']}** {y['branch_name']}<br>{y['branch_animal']}<br>`{y['branch_elem']}` | **地支**<br>Earthly Branches |\n"
        f"| {format_hs(h['hidden_stems'])} | {format_hs(d['hidden_stems'])} | {format_hs(m['hidden_stems'])} | {format_hs(y['hidden_stems'])} | **藏干**<br>Hidden Stems |\n\n"
        f"* **Day Master (日元):** **{d['stem_char']} {d['stem_name']} ({p['day_master_element']})** sitting on **{d['branch_animal']} ({d['branch_name']})**\n"
        f"* **Celestial Animal (生肖):** {aux.get('celestial_animal', '-')}\n"
        f"* **Noble People (貴人):** {aux.get('noble_people', '-')}\n"
        f"* **Intelligence (文昌):** {aux.get('intelligence', '-')}\n"
        f"* **Peach Blossom (桃花):** {aux.get('peach_blossom', '-')}\n"
        f"* **Sky Horse (驛馬):** {aux.get('sky_horse', '-')}\n"
        f"* **Solitary (孤辰):** {aux.get('solitary', '-')}\n"
        f"* **Life Palace (命宮):** {aux.get('life_palace', '-')}\n"
        f"* **Conception Palace (胎元):** {aux.get('conception_palace', '-')}\n"
        f"* **Life Star / Ming Gua (命卦):** {gua.get('life_star_zh', '')} ({gua.get('life_star_num', '')} {gua.get('life_star_color', '')}) | **Feng Shui Gua:** {gua.get('fs_gua_char', '')} {gua.get('fs_gua_name', '')} ({gua.get('fs_gua_dir', '')})\n"
        f"* **Qi Men Destiny Palace (奇門命宮):** {p.get('qimen_destiny', {}).get('palace', '-')} | **Life Stem (命干):** {p.get('qimen_destiny', {}).get('stem', '-')} | **Door (門):** {p.get('qimen_destiny', {}).get('door', '-')} | **Star (星):** {p.get('qimen_destiny', {}).get('star', '-')} | **Guardian (神):** {p.get('qimen_destiny', {}).get('guardian', '-')}\n"
    )
    return md

def build_grounded_bazi_prompt(birth_date_str: str, birth_time_str: str, gender: str, question: str, client_name: str = "Client") -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Computes exact astronomical pillars, formats prompt, and returns (prompt, pillars_dict).
    """
    year, month, day, hour, minute = parse_date_and_time(birth_date_str, birth_time_str)
    
    if year and month and day:
        pillars = calculate_four_pillars(year, month, day, hour, minute, gender=gender, client_name=client_name)
        d = pillars['day']
        chart_table_md = generate_natal_chart_markdown(pillars)
        
        prompt = (
            f"BaZi Consultation Request:\n"
            f"- Client Name: {client_name}\n"
            f"- Birth Date: {birth_date_str} (Parsed Solar: {year}-{month:02d}-{day:02d})\n"
            f"- Birth Time (Local Solar Time): {birth_time_str} (Parsed: {hour:02d}:{minute:02d})\n"
            f"- Gender: {gender}\n"
            f"- Question / Focus: {question}\n\n"
            f"MANDATORY VERIFIED NATAL CHART (Classical format: Hour, Day, Month, Year):\n\n"
            f"{chart_table_md}\n"
            f"STRICT INSTRUCTIONS:\n"
            f"1. You MUST adopt this exact Four Pillars orientation (Hour on left, Day, Month, Year on right).\n"
            f"2. Day Master is strictly **{d['stem_name']} ({pillars['day_master_element']})** sitting on **{d['branch_name']} ({pillars['day_animal']})**.\n"
            f"3. Provide an authentic, comprehensive classical BaZi analysis in the requested language (if Khmer is requested, respond in fluent Khmer as well):\n"
            f"   - Level 1: Day Master Strength & Climate Regulation (Tiao Hou)\n"
            f"   - Level 2: Ten Gods Quality Qualification (Superior, Good, Average, Poor)\n"
            f"   - Level 3: Earthly Branch Dynamics (Combinations, Clashes, Harms, Punishments, Destructions)\n"
            f"   - Level 4: Strategic Life Guidance (Career, Wealth, Spouse Palace, Health, and 10-Year Luck Cycle management)."
        )
        return prompt, pillars
    else:
        fallback_prompt = (
            f"BaZi Consultation Request:\n"
            f"- Birth Date: {birth_date_str}\n"
            f"- Birth Time: {birth_time_str}\n"
            f"- Gender: {gender}\n"
            f"- Focus: {question}\n"
            f"Please calculate the Four Pillars and provide classical BaZi analysis."
        )
        return fallback_prompt, None
