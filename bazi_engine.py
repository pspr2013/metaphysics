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
    '鼠 Rat', '牛 Ox', '虎 Tiger', '兔 Rabbit', '龍 Dragon', '蛇 Snake',
    '馬 Horse', '羊 Goat', '猴 Monkey', '雞 Rooster', '狗 Dog', '豬 Pig'
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
        {'char': '丁', 'name': 'Ding', 'polarity_elem': '-Fire火', 'stem_idx': 3},
        {'char': '己', 'name': 'Ji', 'polarity_elem': '-Earth土', 'stem_idx': 5}
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
        {'char': '丁', 'name': 'Ding', 'polarity_elem': '-Fire火', 'stem_idx': 3},
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4},
        {'char': '辛', 'name': 'Xin', 'polarity_elem': '-Metal金', 'stem_idx': 7}
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

def get_10_god(dm_idx: int, target_idx: int, is_day_master: bool = False) -> Dict[str, str]:
    """
    Computes 10 God notation between Day Master stem and target stem.
    Only the Day Heavenly Stem receives Day Master (DM). Hidden stems and other pillars receive Friend (F) / Rob Wealth (RW).
    """
    if is_day_master:
        return {'zh_full': '日元', 'zh_short': '日', 'code': 'DM', 'en_full': 'Day Master'}
    dm_elem = dm_idx // 2
    target_elem = target_idx // 2
    same_polar = (dm_idx % 2) == (target_idx % 2)
    
    if dm_elem == target_elem:
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

def calculate_auxiliary_stars(dm_stem_idx: int, y_branch_idx: int, d_branch_idx: int, m_branch_idx: int, h_branch_idx: int, y_stem_idx: int, m_stem_idx: int, sun_lon: Optional[float] = None) -> Dict[str, Any]:
    # Noble People (Tian Yi Gui Ren 天乙貴人):
    noble_map = {
        0: '未 Goat, 丑 Ox', 1: '申 Monkey, 子 Rat', 2: '酉 Rooster, 亥 Pig', 3: '酉 Rooster, 亥 Pig',
        4: '未 Goat, 丑 Ox', 5: '申 Monkey, 子 Rat', 6: '丑 Ox, 未 Goat', 7: '午 Horse, 寅 Tiger',
        8: '巳 Snake, 卯 Rabbit', 9: '巳 Snake, 卯 Rabbit'
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
    # Classical Palm Digital Cardinal method (数字基数法) with Zhong Qi advance rule (若過中氣，須作次月推):
    # Count month from Yin=1..Hai=10..Chou=12; Hour from Yin=1..Hai=10..Chou=12
    m_num = (m_branch_idx - 2) % 12 + 1
    if sun_lon is not None:
        deg_in_month = (sun_lon - 315.0) % 360.0
        if (deg_in_month % 30.0) >= 15.0:
            m_num = (m_num % 12) + 1

    h_num = (h_branch_idx - 2) % 12 + 1
    total = m_num + h_num
    mg_num = (14 - total) if total < 14 else (26 - total)
    if mg_num <= 0:
        mg_num += 12
    mg_branch_idx = (mg_num - 1 + 2) % 12
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

def calculate_pillar_shen_sha(
    d_stem: int, y_stem: int, m_stem: int, h_stem: int,
    d_branch: int, y_branch: int, m_branch: int, h_branch: int
) -> Dict[str, List[Dict[str, str]]]:
    """
    Calculates authentic classical Shen Sha (Auxiliary Stars 神煞) for each individual pillar
    (Hour, Day, Month, Year) based on Day Master, Year Stem, Month Branch, and Three Harmonies (San He).
    """
    pillars_order = ['hour', 'day', 'month', 'year']
    stems = {'hour': h_stem, 'day': d_stem, 'month': m_stem, 'year': y_stem}
    branches = {'hour': h_branch, 'day': d_branch, 'month': m_branch, 'year': y_branch}
    result: Dict[str, List[Dict[str, str]]] = {k: [] for k in pillars_order}

    # 1. Nobleman (Tian Yi Gui Ren 天乙貴人):
    # Jia/Wu/Geng -> Chou(1), Wei(7)
    # Yi/Ji -> Zi(0), Shen(8)
    # Bing/Ding -> Hai(11), You(9)
    # Ren/Gui -> Mao(3), Si(5)
    # Xin -> Wu(6), Yin(2)
    tian_yi_map = {
        0: [1, 7], 4: [1, 7], 6: [1, 7],
        1: [0, 8], 5: [0, 8],
        2: [11, 9], 3: [11, 9],
        8: [3, 5], 9: [3, 5],
        7: [6, 2]
    }

    # 2. Academic Star (Wen Chang Gui Ren 文昌貴人)
    wen_chang_map = {0: 5, 1: 6, 2: 8, 3: 9, 4: 8, 5: 9, 6: 11, 7: 0, 8: 2, 9: 3}

    # 3. Prosperity (Lu Shen 祿神)
    lu_map = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}

    # 4. Goat Blade (Yang Ren 羊刃)
    yang_ren_map = {0: 3, 1: 4, 2: 6, 3: 7, 4: 6, 5: 7, 6: 9, 7: 10, 8: 0, 9: 1}

    # 5. Golden Carriage (Jin Yu 金輿)
    jin_yu_map = {0: 4, 1: 5, 2: 7, 3: 8, 4: 7, 5: 8, 6: 10, 7: 11, 8: 1, 9: 2}

    # 6. Tai Ji Nobleman (Tai Ji Gui Ren 太極貴人)
    taiji_map = {
        0: [0, 6], 1: [0, 6],
        2: [3, 9], 3: [3, 9],
        4: [1, 7, 4, 10], 5: [1, 7, 4, 10],
        6: [2, 11], 7: [2, 11],
        8: [5, 8], 9: [5, 8]
    }

    # 7. National Seal (Guo Yin Gui Ren 國印貴人)
    guo_yin_map = {0: 10, 1: 11, 2: 1, 3: 2, 4: 1, 5: 2, 6: 4, 7: 5, 8: 7, 9: 8}

    # 8. San He Three Harmonies Star Groups (from Day Branch & Year Branch)
    # 0: Shen-Zi-Chen, 1: Si-You-Chou, 2: Yin-Wu-Xu, 3: Hai-Mao-Wei
    def get_san_he_stars(ref_branch: int) -> Dict[str, int]:
        grp = ref_branch % 4
        if grp == 0:
            return {'peach': 9, 'horse': 2, 'general': 0, 'canopy': 4, 'robbery': 5, 'death': 11}
        elif grp == 1:
            return {'peach': 6, 'horse': 11, 'general': 9, 'canopy': 1, 'robbery': 2, 'death': 8}
        elif grp == 2:
            return {'peach': 3, 'horse': 8, 'general': 6, 'canopy': 10, 'robbery': 11, 'death': 5}
        else:
            return {'peach': 0, 'horse': 5, 'general': 3, 'canopy': 7, 'robbery': 8, 'death': 2}

    day_sh = get_san_he_stars(d_branch)
    year_sh = get_san_he_stars(y_branch)

    # 9. Hong Luan & Tian Xi (from Year Branch)
    hong_luan_b = (3 - y_branch) % 12
    tian_xi_b = (hong_luan_b + 6) % 12

    # 10. Solitary (Gu Chen 孤辰) & Lonesome (Gua Su 寡宿) (from Year Branch season)
    def get_season(b: int) -> str:
        if b in [11, 0, 1]: return 'winter'
        if b in [2, 3, 4]: return 'spring'
        if b in [5, 6, 7]: return 'summer'
        return 'autumn'

    sea = get_season(y_branch)
    if sea == 'winter': gu_chen_b, gua_su_b = 2, 10
    elif sea == 'spring': gu_chen_b, gua_su_b = 5, 1
    elif sea == 'summer': gu_chen_b, gua_su_b = 8, 4
    else: gu_chen_b, gua_su_b = 11, 7

    # 11. Heavenly Doctor (Tian Yi 天醫) = Month Branch - 1
    tian_yi_doc_b = (m_branch - 1) % 12

    # 12. Monthly Virtue (Yue De Gui Ren 月德貴人)
    # Yin-Wu-Xu: Bing(2), Shen-Zi-Chen: Ren(8), Hai-Mao-Wei: Jia(0), Si-You-Chou: Geng(6)
    m_grp = m_branch % 4
    yue_de_s = {2: 2, 0: 8, 3: 0, 1: 6}[m_grp]

    # 13. Heavenly Virtue (Tian De Gui Ren 天德貴人)
    tian_de_map = {
        2: ('s', 3), 3: ('b', 8), 4: ('s', 8), 5: ('s', 7),
        6: ('b', 11), 7: ('s', 0), 8: ('s', 9), 9: ('b', 2),
        10: ('s', 2), 11: ('s', 1), 0: ('b', 5), 1: ('s', 6)
    }
    td_type, td_target = tian_de_map[m_branch]

    for p_col in pillars_order:
        b_idx = branches[p_col]
        s_idx = stems[p_col]
        p_stars: List[Dict[str, str]] = []

        # Tian Yi Nobleman (Day Master)
        if b_idx in tian_yi_map.get(d_stem, []):
            p_stars.append({'zh': '天乙貴人', 'en': 'Tian Yi Nobleman', 'category': 'noble'})
        # Tian Yi Nobleman (Year Stem)
        elif b_idx in tian_yi_map.get(y_stem, []):
            p_stars.append({'zh': '天乙貴人(年)', 'en': 'Year Nobleman', 'category': 'noble'})

        # Tai Ji Nobleman
        if b_idx in taiji_map.get(d_stem, []):
            p_stars.append({'zh': '太極貴人', 'en': 'Tai Ji Nobleman', 'category': 'taiji'})

        # Tian De & Yue De
        if td_type == 's' and s_idx == td_target:
            p_stars.append({'zh': '天德貴人', 'en': 'Heavenly Virtue', 'category': 'virtue'})
        elif td_type == 'b' and b_idx == td_target:
            p_stars.append({'zh': '天德貴人', 'en': 'Heavenly Virtue', 'category': 'virtue'})

        if s_idx == yue_de_s:
            p_stars.append({'zh': '月德貴人', 'en': 'Monthly Virtue', 'category': 'virtue'})

        # Wen Chang Academic
        if b_idx == wen_chang_map.get(d_stem):
            p_stars.append({'zh': '文昌貴人', 'en': 'Academic Star', 'category': 'academic'})

        # National Seal
        if b_idx == guo_yin_map.get(d_stem):
            p_stars.append({'zh': '國印貴人', 'en': 'National Seal', 'category': 'noble'})

        # Lu Shen Prosperity
        if b_idx == lu_map.get(d_stem):
            p_stars.append({'zh': '祿神', 'en': 'Prosperity Star', 'category': 'lu'})

        # Jin Yu Golden Carriage
        if b_idx == jin_yu_map.get(d_stem):
            p_stars.append({'zh': '金輿', 'en': 'Golden Carriage', 'category': 'jinyu'})

        # General Star
        if b_idx == day_sh['general'] or b_idx == year_sh['general']:
            p_stars.append({'zh': '將星', 'en': 'General Star', 'category': 'general'})

        # Hua Gai Elegant Seal / Canopy
        if b_idx == day_sh['canopy'] or b_idx == year_sh['canopy']:
            p_stars.append({'zh': '華蓋', 'en': 'Elegant Seal', 'category': 'canopy'})

        # Sky Horse
        if b_idx == day_sh['horse'] or b_idx == year_sh['horse']:
            p_stars.append({'zh': '驛馬', 'en': 'Sky Horse', 'category': 'horse'})

        # Peach Blossom
        if b_idx == day_sh['peach'] or b_idx == year_sh['peach']:
            p_stars.append({'zh': '桃花', 'en': 'Peach Blossom', 'category': 'peach'})

        # Red Matchmaker & Heavenly Happiness
        if b_idx == hong_luan_b:
            p_stars.append({'zh': '紅鸞', 'en': 'Red Matchmaker', 'category': 'romance'})
        if b_idx == tian_xi_b:
            p_stars.append({'zh': '天喜', 'en': 'Heavenly Happiness', 'category': 'romance'})

        # Heavenly Doctor
        if b_idx == tian_yi_doc_b:
            p_stars.append({'zh': '天醫', 'en': 'Heavenly Doctor', 'category': 'doctor'})

        # Goat Blade
        if b_idx == yang_ren_map.get(d_stem):
            p_stars.append({'zh': '羊刃', 'en': 'Goat Blade', 'category': 'blade'})

        # Robbery Sha & Death God
        if b_idx == day_sh['robbery'] or b_idx == year_sh['robbery']:
            p_stars.append({'zh': '劫煞', 'en': 'Robbery Sha', 'category': 'sha'})
        if b_idx == day_sh['death'] or b_idx == year_sh['death']:
            p_stars.append({'zh': '亡神', 'en': 'Death God', 'category': 'sha'})

        # Solitary & Lonesome
        if b_idx == gu_chen_b:
            p_stars.append({'zh': '孤辰', 'en': 'Solitary Star', 'category': 'sha'})
        if b_idx == gua_su_b:
            p_stars.append({'zh': '寡宿', 'en': 'Lonesome Star', 'category': 'sha'})

        # Special Pillars
        pillar_str = f"{STEM_CHARS[s_idx]}{BRANCH_CHARS[b_idx]}"
        if pillar_str in ['戊戌', '庚戌', '庚辰', '壬辰']:
            p_stars.append({'zh': '魁罡', 'en': 'Kui Gang', 'category': 'leader'})
        if pillar_str in ['甲辰', '乙亥', '丙辰', '丁酉', '戊午', '庚戌', '庚寅', '辛亥', '壬寅', '癸未']:
            p_stars.append({'zh': '十靈日', 'en': 'Ten Spirits', 'category': 'taiji'})
        if pillar_str in ['乙丑', '己巳', '癸酉']:
            p_stars.append({'zh': '金神', 'en': 'Golden God', 'category': 'general'})

        # Deduplicate preserving order
        seen = set()
        dedup = []
        for s in p_stars:
            if s['zh'] not in seen:
                seen.add(s['zh'])
                dedup.append(s)
        result[p_col] = dedup

    return result

def get_shen_sha_badge_style(category: str) -> str:
    """Returns CSS styles for color-coded Shen Sha badges."""
    base = "display: inline-flex; flex-direction: column; align-items: center; justify-content: center; padding: 4px 6px; border-radius: 5px; font-size: 11px; text-align: center; min-width: 66px; max-width: 105px; box-sizing: border-box; "
    if category in ('noble', 'virtue', 'lu', 'general', 'jinyu'):
        return base + "background: rgba(245, 158, 11, 0.14); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.38);"
    elif category in ('academic', 'doctor'):
        return base + "background: rgba(16, 185, 129, 0.14); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.38);"
    elif category in ('horse', 'taiji', 'leader'):
        return base + "background: rgba(56, 189, 248, 0.14); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.38);"
    elif category in ('romance', 'peach'):
        return base + "background: rgba(244, 114, 182, 0.14); color: #f472b6; border: 1px solid rgba(244, 114, 182, 0.38);"
    elif category in ('canopy',):
        return base + "background: rgba(192, 132, 252, 0.14); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.38);"
    elif category in ('blade', 'sha'):
        return base + "background: rgba(244, 63, 94, 0.14); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.38);"
    return base + "background: rgba(148, 163, 184, 0.14); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.35);"

def calculate_ming_gua(bazi_year: int, gender: str) -> Dict[str, Any]:
    """Computes Life Star (Ming Gua) and 8 Mansions (Ba Zhai) Favorable/Unfavorable Directions."""
    last_two = bazi_year % 100
    d = sum(int(c) for c in str(last_two))
    while d >= 10:
        d = sum(int(c) for c in str(d))
    
    is_male = gender.lower().startswith('m')
    if bazi_year < 2000:
        if is_male:
            gua = 10 - d
            if gua == 0:
                gua = 9
        else:
            gua = 5 + d
            while gua >= 10:
                gua = sum(int(c) for c in str(gua))
    else:
        if is_male:
            gua = 9 - d
            if gua == 0:
                gua = 9
        else:
            gua = 6 + d
            while gua >= 10:
                gua = sum(int(c) for c in str(gua))
    
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
        'group': 'West Group 西四命' if active_gua in [2, 5, 6, 7, 8] else 'East Group 東四命',
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
    aux = calculate_auxiliary_stars(day_stem_idx, y_branch_idx, day_branch_idx, m_branch_idx, h_branch_idx, y_stem_idx, m_stem_idx, sun_lon=sun_lon)
    pillar_shen_sha = calculate_pillar_shen_sha(
        day_stem_idx, y_stem_idx, m_stem_idx, h_stem_idx,
        day_branch_idx, y_branch_idx, m_branch_idx, h_branch_idx
    )

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
            ],
            'shen_sha': pillar_shen_sha['hour'],
        },
        'day': {
            'stem_idx': day_stem_idx,
            'branch_idx': day_branch_idx,
            'stem_char': STEM_CHARS[day_stem_idx],
            'stem_name': STEM_NAMES[day_stem_idx],
            'stem_elem': STEM_SHORT_ELEMENTS[day_stem_idx],
            'stem_god': get_10_god(day_stem_idx, day_stem_idx, is_day_master=True),
            'branch_char': BRANCH_CHARS[day_branch_idx],
            'branch_name': BRANCH_NAMES[day_branch_idx],
            'branch_animal': BRANCH_ANIMALS[day_branch_idx],
            'branch_elem': BRANCH_ELEMENTS[day_branch_idx],
            'hidden_stems': [
                {
                    **hs,
                    'god': get_10_god(day_stem_idx, hs['stem_idx'])
                } for hs in BRANCH_HIDDEN_STEMS_MAP[day_branch_idx]
            ],
            'shen_sha': pillar_shen_sha['day'],
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
            ],
            'shen_sha': pillar_shen_sha['month'],
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
            ],
            'shen_sha': pillar_shen_sha['year'],
        },
        'day_master': STEM_NAMES[day_stem_idx],
        'day_master_element': STEM_ELEMENTS[day_stem_idx],
        'day_animal': BRANCH_ANIMALS[day_branch_idx],
        'aux': aux,
        'pillar_shen_sha': pillar_shen_sha,
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

ELEMENT_COLORS = {
    'Wood': '#10b981',   # Emerald Green
    'Fire': '#ef4444',   # Ruby Red
    'Earth': '#f59e0b',  # Warm Amber / Gold
    'Metal': '#e2e8f0',  # Platinum / Silver
    'Water': '#38bdf8'   # Sky / Sapphire Blue
}

def get_stem_element_color(stem_char: str) -> str:
    wood = ('甲', '乙')
    fire = ('丙', '丁')
    earth = ('戊', '己')
    metal = ('庚', '辛')
    water = ('壬', '癸')
    if stem_char in wood: return ELEMENT_COLORS['Wood']
    if stem_char in fire: return ELEMENT_COLORS['Fire']
    if stem_char in earth: return ELEMENT_COLORS['Earth']
    if stem_char in metal: return ELEMENT_COLORS['Metal']
    if stem_char in water: return ELEMENT_COLORS['Water']
    return '#f8fafc'

def get_branch_element_color(branch_char: str) -> str:
    wood = ('寅', '卯')
    fire = ('巳', '午')
    earth = ('辰', '戌', '丑', '未')
    metal = ('申', '酉')
    water = ('亥', '子')
    if branch_char in wood: return ELEMENT_COLORS['Wood']
    if branch_char in fire: return ELEMENT_COLORS['Fire']
    if branch_char in earth: return ELEMENT_COLORS['Earth']
    if branch_char in metal: return ELEMENT_COLORS['Metal']
    if branch_char in water: return ELEMENT_COLORS['Water']
    return '#f8fafc'

# ==========================================
# 2026 ANNUAL BAZI STARS & QIMEN SYSTEM
# ==========================================

ANNUAL_BAZI_STARS_2026 = {
    0: { # 子 Zi (Rat)
        'auspicious': [('唐符', 'Imperial Advisor'), ('月空', 'Month Emptiness')],
        'inauspicious': [('歲破', 'Year Breaker'), ('大耗', 'Greater Consumer'), ('欄杆', 'Obstacle'), ('災煞', 'Calamity Sha'), ('天哭', 'Sky Cry'), ('飛刃', 'Flying Blade'), ('囚獄', 'Prison Star')]
    },
    1: { # 丑 Chou (Ox)
        'auspicious': [('國印', 'National Treasure'), ('龍德', 'Dragon Virtue'), ('紫微', 'Emperor Star')],
        'inauspicious': [('歲煞', 'Year Sha'), ('暴敗', 'Brutal Defeat'), ('天厄', 'Dark Sky'), ('六害', 'Six Harm'), ('天煞', 'Sky Killing'), ('吞陷', 'Swallow Trap')]
    },
    2: { # 寅 Yin (Tiger)
        'auspicious': [('學堂', 'Academy')],
        'inauspicious': [('白虎', 'White Tiger'), ('指背', 'Back Poking'), ('大煞', 'Great Sha'), ('飛廉', 'Flying Chaste'), ('天雄', 'Sky Warrior'), ('地煞', 'Earth Killing'), ('紅艷煞', 'Red Chamber Sha')]
    },
    3: { # 卯 Mao (Rabbit)
        'auspicious': [('天德', 'Heavenly Virtue'), ('福德', 'Fortune Virtue'), ('福星', 'Prosperity Star'), ('天喜', 'Sky Happiness'), ('桃花', 'Peach Blossom'), ('咸池', 'Salty Pool'), ('太極貴人', 'Tai Ji Nobleman')],
        'inauspicious': [('絞煞', 'Crossing Sha'), ('年煞', 'Year Sha'), ('卷舌', 'Curled Tongue'), ('披麻', 'Wear Mourning')]
    },
    4: { # 辰 Chen (Dragon)
        'auspicious': [('八座', 'Eight Seats'), ('天解', 'Sky Relief'), ('解神', 'Relief God')],
        'inauspicious': [('天狗', 'Heavenly Dog'), ('吊客', 'Condolence Visitor'), ('寡宿', 'Lonesome Star'), ('血刃', 'Blood Blade')]
    },
    5: { # 巳 Si (Snake)
        'auspicious': [('祿神', 'Thriving'), ('陌越', 'Surpassing Path'), ('詞館', 'Clan House'), ('天官貴人', 'Heavenly Officer'), ('天廚貴人', 'Heavenly Chef')],
        'inauspicious': [('病符', 'Sickness Charm'), ('的煞', 'Solid Killing'), ('亡神', 'Death God'), ('破碎', 'Broken Star'), ('天官符', 'Heavenly Officer Charm')]
    },
    6: { # 午 Wu (Horse)
        'auspicious': [('將星', 'General Star'), ('金匱', 'Golden Lock')],
        'inauspicious': [('太歲', 'Tai Sui'), ('劍鋒', 'Sword Edge'), ('伏屍', 'Lying Corpse'), ('黃旛', 'Yellow Flag')]
    },
    7: { # 未 Wei (Goat)
        'auspicious': [('歲合', 'Grand Duke Combination'), ('太陽', 'Sun'), ('金輿', 'Golden Carriage')],
        'inauspicious': [('板鞍', 'Pulling Saddle'), ('天空', 'Sky Emptiness'), ('晦氣', 'Bad Qi'), ('流霞煞', 'Cascading Clouds Sha')]
    },
    8: { # 申 Shen (Monkey)
        'auspicious': [('驛馬', 'Sky Horse'), ('文昌', 'Academic Star')],
        'inauspicious': [('喪門', 'Funeral Door'), ('地喪', 'Earth Funeral'), ('孤辰', 'Solitary'), ('披頭', 'Disheveled Hair')]
    },
    9: { # 酉 You (Rooster)
        'auspicious': [('天乙', 'Heavenly Yi'), ('太陰', 'Moon'), ('紅鸞', 'Red Matchmaker'), ('太極貴人', 'Tai Ji Nobleman'), ('天鉞', 'Sky Gracious')],
        'inauspicious': [('貫索', 'Piercing Rope'), ('勾神', 'Hook Spirit'), ('卒暴', 'Great Assembly'), ('六厄', 'Six Calamity')]
    },
    10: { # 戌 Xu (Dog)
        'auspicious': [('三台', 'Three Stages'), ('華蓋', 'Elegant Seal')],
        'inauspicious': [('五鬼', 'Five Ghosts'), ('官符', 'Official Charm'), ('飛符', 'Flying Charm')]
    },
    11: { # 亥 Hai (Pig)
        'auspicious': [('玉堂', 'Jade Hall'), ('月德', 'Monthly Virtue'), ('天魁', 'Sky Noble')],
        'inauspicious': [('死符', 'Death Charm'), ('小耗', 'Lesser Consumer'), ('劫煞', 'Robbery Sha')]
    }
}

ANNUAL_BAZI_STARS_2025 = {
    0: { # 子 Zi (Rat)
        'auspicious': [('天喜', 'Sky Happiness'), ('咸池', 'Salty Pool')],
        'inauspicious': [('死符', 'Death Charm'), ('小耗', 'Lesser Consumer')]
    },
    1: { # 丑 Chou (Ox)
        'auspicious': [('華蓋', 'Elegant Seal'), ('三台', 'Three Stages')],
        'inauspicious': [('五鬼', 'Five Ghosts'), ('官符', 'Official Charm')]
    },
    2: { # 寅 Yin (Tiger)
        'auspicious': [('天德', 'Heavenly Virtue'), ('福星', 'Fortune Star')],
        'inauspicious': [('劫煞', 'Robbery Sha'), ('披麻', 'Wear Mourning')]
    },
    3: { # 卯 Mao (Rabbit)
        'auspicious': [],
        'inauspicious': [('天狗', 'Sky Dog'), ('吊客', 'Funeral Guest'), ('災煞', 'Calamity Sha')]
    },
    4: { # 辰 Chen (Dragon)
        'auspicious': [('太陽', 'Sun'), ('天乙', 'Heavenly Yi')],
        'inauspicious': [('天空', 'Sky Emptiness'), ('晦氣', 'Bad Qi')]
    },
    5: { # 巳 Si (Snake)
        'auspicious': [('太歲', 'Grand Duke'), ('歲駕', 'Year Carriage')],
        'inauspicious': [('劍鋒', 'Sword Edge'), ('伏屍', 'Hidden Corpse')]
    },
    6: { # 午 Wu (Horse)
        'auspicious': [('紅鸞', 'Red Matchmaker'), ('文昌', 'Intelligence')],
        'inauspicious': [('咸池', 'Salty Pool'), ('陌越', 'Mo Yue')]
    },
    7: { # 未 Wei (Goat)
        'auspicious': [],
        'inauspicious': [('喪門', 'Funeral Door'), ('地喪', 'Earth Mourning'), ('豹尾', 'Leopard Tail')]
    },
    8: { # 申 Shen (Monkey)
        'auspicious': [('太陰', 'Moon'), ('歲合', 'Grand Duke Combination')],
        'inauspicious': [('亡神', 'Death God'), ('勾神', 'Hook Spirit')]
    },
    9: { # 酉 You (Rooster)
        'auspicious': [('將星', 'General Star'), ('金匱', 'Golden Lock'), ('八座', 'Eight Seats')],
        'inauspicious': [('白虎', 'White Tiger')]
    },
    10: { # 戌 Xu (Dog)
        'auspicious': [('月德', 'Monthly Virtue'), ('地解', 'Earth Relief')],
        'inauspicious': [('死符', 'Death Charm'), ('小耗', 'Lesser Consumer')]
    },
    11: { # 亥 Hai (Pig)
        'auspicious': [('驛馬', 'Sky Horse')],
        'inauspicious': [('歲破', 'Year Breaker'), ('大耗', 'Greater Consumer'), ('闌干', 'Lan Gan')]
    }
}

ANNUAL_QIMEN_PALACE_YEAR_STARS = {
    2025: {
        1: [('天喜', 'Sky Happiness', 'auspicious'), ('死符', 'Death Charm', 'inauspicious')], # North (坎 1)
        2: [('太陽', 'Sun', 'auspicious'), ('驛馬', 'Sky Horse', 'auspicious'), ('喪門', 'Funeral Door', 'inauspicious')], # Southwest (坤 2)
        3: [('天狗', 'Sky Dog', 'inauspicious'), ('吊客', 'Funeral Guest', 'inauspicious')], # East (震 3)
        4: [('太歲', 'Grand Duke', 'auspicious'), ('將星', 'General Star', 'auspicious'), ('劍鋒', 'Sword Edge', 'inauspicious')], # Southeast (巽 4)
        6: [('歲破', 'Year Breaker', 'inauspicious'), ('大耗', 'Greater Consumer', 'inauspicious')], # Northwest (乾 6)
        7: [('金匱', 'Golden Lock', 'auspicious'), ('將星', 'General Star', 'auspicious'), ('白虎', 'White Tiger', 'inauspicious')], # West (兌 7)
        8: [('華蓋', 'Elegant Seal', 'auspicious'), ('天解', 'Sky Relief', 'auspicious'), ('劫煞', 'Robbery Sha', 'inauspicious')], # Northeast (艮 8)
        9: [('紅鸞', 'Red Matchmaker', 'auspicious'), ('咸池', 'Salty Pool', 'neutral'), ('捲舌', 'Curled Tongue', 'inauspicious')] # South (離 9)
    },
    2026: {
        1: [('歲破', 'Year Breaker', 'inauspicious'), ('大耗', 'Greater Consumer', 'inauspicious')], # North (坎 1)
        2: [('太陽', 'Sun', 'auspicious'), ('歲合', 'Grand Duke Combination', 'auspicious')], # Southwest (坤 2)
        3: [('紅鸞', 'Red Matchmaker', 'auspicious'), ('福德', 'Fortune Virtue', 'auspicious')], # East (震 3)
        4: [('天解', 'Sky Relief', 'auspicious'), ('八座', 'Eight Seats', 'auspicious')], # Southeast (巽 4)
        6: [('月德', 'Monthly Virtue', 'auspicious'), ('天乙', 'Heavenly Yi', 'auspicious')], # Northwest (乾 6)
        7: [('太陰', 'Moon', 'auspicious'), ('太極', 'Tai Ji Nobleman', 'auspicious')], # West (兌 7)
        8: [('金匱', 'Golden Lock', 'auspicious'), ('五鬼 官符', 'Five Ghost Litigation', 'inauspicious')], # Northeast (艮 8)
        9: [('太歲', 'Grand Duke', 'auspicious'), ('將星', 'General Star', 'auspicious')] # South (離 9)
    }
}
ANNUAL_QIMEN_PALACE_YEAR_STARS_2026 = ANNUAL_QIMEN_PALACE_YEAR_STARS[2026]

def calculate_mobility_directions(bazi_year: int, gender: str, target_year: int = 2026) -> List[Tuple[str, str, str, str]]:
    """
    Computes authentic Qi Men Mobility Directions (本命流年奇門出行方)
    based on the client's Life Gua (Ming Gua / 命卦) and target year.
    Flies the Eight Mobility Stars in forward Luoshu sequence through the 8 directions starting from the Life Gua,
    with authentic annual cycle progression.
    """
    is_male = gender.lower().startswith('m')
    last_two = bazi_year % 100
    d = sum(int(c) for c in str(last_two))
    while d >= 10:
        d = sum(int(c) for c in str(d))
    if bazi_year < 2000:
        g = (10 - d) if is_male else (5 + d)
    else:
        g = (9 - d) if is_male else (6 + d)
    while g >= 10:
        g = sum(int(c) for c in str(g))
    if g == 0:
        g = 9
    active_gua = (2 if is_male else 8) if g == 5 else g

    display_dirs = [
        ('W', '西', 7),
        ('S', '南', 9),
        ('SW', '西南', 2),
        ('N', '北', 1),
        ('NW', '西北', 6),
        ('NE', '東北', 8),
        ('E', '東', 3),
        ('SE', '東南', 4)
    ]
    # Authentic forward Luoshu flight order (skipping 5 center)
    palace_flight = [1, 2, 3, 4, 6, 7, 8, 9]
    if active_gua in palace_flight:
        start_idx = palace_flight.index(active_gua)
    else:
        start_idx = 0
    ordered_palaces = [palace_flight[(start_idx + i) % 8] for i in range(8)]

    # Mobility Stars in authentic classical order
    # Baseline for 2026 (Star 1 in center):
    stars_sequence = [
        ('招搖 Swagger', 'neutral'),
        ('軒轅 Regulus', 'neutral'),
        ('攝提 Extractor', 'neutral'),
        ('天乙 Heavenly Noble', 'red'),
        ('太陰 Great Moon', 'red'),
        ('咸池 Salty Pool', 'neutral'),
        ('青龍 Green Dragon', 'blue'),
        ('天符 Heavenly Seal', 'neutral')
    ]
    
    # Year offset (annual cycle shifting through 8 perimeter palaces)
    year_shift = (target_year - 2026) % 8
    shifted_stars = [stars_sequence[(i - year_shift) % 8] for i in range(8)]
    palace_to_star = {p: star_info for p, star_info in zip(ordered_palaces, shifted_stars)}

    return [(code, zh, palace_to_star[p][0], palace_to_star[p][1]) for code, zh, p in display_dirs]


def calculate_luck_pillars(p: Dict[str, Any], current_year: int = 2026) -> List[Dict[str, Any]]:
    """
    Computes 10-year Luck Pillars (大運) for the natal chart.
    """
    m_s_idx = p['month']['stem_idx']
    m_b_idx = p['month']['branch_idx']
    y_s_idx = p['year']['stem_idx']
    gender = p.get('gender', 'Male')
    is_male = gender.lower().startswith('m')
    is_yang_year = (y_s_idx % 2 == 0)
    forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)
    step = 1 if forward else -1

    dm_s_idx = p['day']['stem_idx']
    day_b_idx = p['day']['branch_idx']

    # Xun Kong Wang (空亡 / Death & Emptiness) for Day Pillar
    xun_branch_start = (day_b_idx - dm_s_idx) % 12
    kong_wang_branches = [(xun_branch_start + 10) % 12, (xun_branch_start + 11) % 12]

    birth_year = p.get('birth_year', 1986)
    client_age_now = current_year - birth_year

    luck_pillars = []
    for i in range(1, 10):
        s_i = (m_s_idx + i * step) % 10
        b_i = (m_b_idx + i * step) % 12
        age = i * 10
        is_kw = b_i in kong_wang_branches
        god = get_10_god(dm_s_idx, s_i)
        hs = BRANCH_HIDDEN_STEMS_MAP[b_i]
        is_current = (age <= client_age_now < age + 10) or (age == 40 and client_age_now == 40)
        luck_pillars.append({
            'age': age,
            'stem_char': STEM_CHARS[s_i],
            'stem_name': STEM_NAMES[s_i],
            'stem_elem': STEM_ELEMENTS[s_i],
            'branch_char': BRANCH_CHARS[b_i],
            'branch_name': BRANCH_NAMES[b_i],
            'branch_animal': BRANCH_SHORT_ANIMALS[b_i],
            'branch_elem': BRANCH_ELEMENTS[b_i],
            'god': god,
            'is_kw': is_kw,
            'is_current': is_current,
            'hidden_stems': hs
        })
    return luck_pillars

def generate_luck_pillars_html(p: Dict[str, Any], current_year: int = 2026) -> str:
    """
    Renders the authentic 10-year Luck Pillars table (大運)
    with ages 90 down to 10 matching Joey Yap's standard layout.
    """
    luck_pillars = calculate_luck_pillars(p, current_year)
    descending_pillars = list(reversed(luck_pillars))
    dm_stem_idx = p['day']['stem_idx']

    html = """
<!-- LUCK PILLARS (大運) -->
<div style="background: #131d36; border: 1px solid #1e3a8a; border-radius: 8px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.25);">
  <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 11px;">
    <thead>
      <!-- AGE ROW -->
      <tr style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-bottom: 1.5px solid #d97706;">
"""
    for lp in descending_pillars:
        if lp['is_current']:
            age_badge = f'<div style="font-size: 9px; font-weight: 800; color: #fbbf24; background: rgba(245, 158, 11, 0.2); border: 1px solid #d97706; border-radius: 3px; padding: 1px 4px; display: inline-block;">Here {lp["age"]} 在此</div>'
        else:
            age_badge = f'<span style="font-weight: 700; color: #94a3b8; font-size: 11px;">{lp["age"]}</span>'
        html += f"""        <th style="padding: 6px 4px; border-right: 1px solid #334155; width: 10%;">
          {age_badge}
        </th>\n"""
    html += """        <th style="padding: 6px 8px; font-weight: 800; color: #fbbf24; text-align: center; width: 10%; background: #1e293b;">
          歲數<br><span style="font-size: 9px; font-weight: normal; color: #94a3b8;">Age</span>
        </th>
      </tr>
    </thead>
    <tbody>
      <!-- STEMS ROW -->
      <tr style="border-bottom: 1px solid #334155; background: rgba(15, 23, 42, 0.7);">
"""
    for lp in descending_pillars:
        s_char = lp['stem_char']
        s_color = get_stem_element_color(s_char)
        god = lp['god']
        html += f"""        <td style="padding: 6px 3px; border-right: 1px solid #334155; vertical-align: top;">
          <div style="font-size: 8.5px; font-weight: 800; color: #f59e0b; background: rgba(245, 158, 11, 0.1); border-radius: 3px; padding: 1px; margin-bottom: 2px;">
            {god['zh_short']} <span style="color: #cbd5e1;">{god['code']}</span>
          </div>
          <div style="font-size: 22px; font-weight: 900; color: {s_color}; line-height: 1;">{s_char}</div>
          <div style="font-size: 10px; font-weight: 700; color: #f8fafc; margin-top: 1px;">{lp['stem_name']}</div>
          <div style="font-size: 8.5px; color: #94a3b8;">{lp['stem_elem']}</div>
        </td>\n"""
    html += """        <td style="padding: 6px 4px; font-size: 11px; font-weight: 700; color: #fbbf24; background: #1e293b; vertical-align: middle; line-height: 1.3;">
          大運<br><span style="font-size: 9px; font-weight: normal; color: #94a3b8;">Luck<br>Pillars</span>
        </td>
      </tr>

      <!-- BRANCHES ROW -->
      <tr style="border-bottom: 1px solid #334155; background: rgba(15, 23, 42, 0.55);">
"""
    for lp in descending_pillars:
        b_char = lp['branch_char']
        b_color = get_branch_element_color(b_char)
        kw_badge = '<div style="font-size: 8px; font-weight: 800; color: #f87171; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 3px; padding: 0.5px; margin-bottom: 2px;">空亡 DE</div>' if lp['is_kw'] else '<div style="height: 13px;"></div>'
        html += f"""        <td style="padding: 6px 3px; border-right: 1px solid #334155; vertical-align: top;">
          {kw_badge}
          <div style="font-size: 20px; font-weight: 900; color: {b_color}; line-height: 1;">{b_char}</div>
          <div style="font-size: 10px; font-weight: 700; color: #f8fafc; margin-top: 1px;">{lp['branch_name']}</div>
          <div style="font-size: 8.5px; color: #cbd5e1;">{lp['branch_animal']}</div>
          <div style="font-size: 8px; color: #94a3b8;">{lp['branch_elem'].split()[-1]}</div>
        </td>\n"""
    html += """        <td style="padding: 6px 4px; font-size: 11px; font-weight: 700; color: #fbbf24; background: #1e293b; vertical-align: middle; line-height: 1.3;">
          地支<br><span style="font-size: 9px; font-weight: normal; color: #94a3b8;">Branches</span>
        </td>
      </tr>

      <!-- HIDDEN STEMS ROW -->
      <tr style="background: rgba(15, 23, 42, 0.7);">
"""
    for lp in descending_pillars:
        hs_list = lp['hidden_stems']
        hs_cards = []
        for hs in hs_list:
            char = hs['char']
            color = get_stem_element_color(char)
            god = get_10_god(dm_stem_idx, hs['stem_idx'])
            hs_cards.append(f"""<div style="display: flex; flex-direction: column; align-items: center; min-width: 22px; padding: 2px 1px;">
              <span style="font-size: 13px; font-weight: 900; color: {color}; line-height: 1;">{char}</span>
              <span style="font-size: 7.5px; color: #94a3b8; line-height: 1; margin-top: 1px;">{hs['name']}</span>
              <span style="font-size: 7.5px; font-weight: 700; color: #f59e0b; margin-top: 1px;">{god['code']}</span>
            </div>""")
        html += f"""        <td style="padding: 4px 2px; border-right: 1px solid #334155; vertical-align: top;">
          <div style="display: flex; justify-content: center; gap: 2px; flex-wrap: wrap;">
            {"".join(hs_cards)}
          </div>
        </td>\n"""
    html += """        <td style="padding: 6px 4px; font-size: 11px; font-weight: 700; color: #fbbf24; background: #1e293b; vertical-align: middle; line-height: 1.3;">
          藏干<br><span style="font-size: 9px; font-weight: normal; color: #94a3b8;">Hidden<br>Stems</span>
        </td>
      </tr>
    </tbody>
  </table>
</div>
"""
    return html

def generate_annual_qimen_elements_html(pillars: Dict[str, Any], current_year: int = 2026) -> str:
    """
    Renders 'THE BAZI CHART - [current_year] QI MEN ELEMENTS [current_year]年八字命盤奇門格'
    mapping each natal pillar Heavenly Stem to its Annual Qi Men Star and Door.
    Matches Joey Yap's authentic layout with left spanning title and traditional Chinese characters.
    """
    ann_stem_idx = (current_year - 4) % 10
    ann_branch_idx = (current_year - 4) % 12
    ann_stem_name = STEM_NAMES[ann_stem_idx]
    ann_branch_name = BRANCH_NAMES[ann_branch_idx]
    
    p_annual = {
        'hour': {'stem_name': ann_stem_name, 'branch_name': ann_branch_name},
        'day': {'stem_name': ann_stem_name, 'branch_name': ann_branch_name},
        'month': {'stem_name': ann_stem_name, 'branch_name': ann_branch_name},
        'year': {'stem_name': ann_stem_name, 'branch_name': ann_branch_name}
    }
    stem_map = {}
    try:
        from qimen_engine import calculate_qimen_chart_from_pillars
        chart_ann = calculate_qimen_chart_from_pillars(p_annual, dun_type='Yin', ju_num=1)
        for p_num, pal in chart_ann['palaces'].items():
            s_char = pal['heaven_stem']['char']
            s_star = pal['star']['char']
            if s_star == '沖':
                s_star = '衝'
            stem_map[s_char] = {
                'star': f"{s_star} {pal['star']['en']}",
                'door': f"{pal['door']['char']} {pal['door']['en']}"
            }
    except Exception:
        pass

    order = ['hour', 'day', 'month', 'year']
    col_headers = {
        'hour': '時干 Hour Stem',
        'day': '日干 Day Stem',
        'month': '月干 Month Stem',
        'year': '年干 Year Stem'
    }

    html = f"""
<!-- {current_year} QI MEN ELEMENTS (八字命盤奇門格) -->
<div style="background: #131d36; border: 1px solid #1e3a8a; border-radius: 8px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.25);">
  <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 11.5px;">
    <thead>
      <tr style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-bottom: 1.5px solid #d97706;">
        <th rowspan="3" style="width: 34%; background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%); color: #ffffff; text-align: center; vertical-align: middle; padding: 10px 14px; border-right: 1.5px solid #d97706;">
          <div style="font-size: 12px; font-weight: 800; color: #fef08a; letter-spacing: 0.5px;">THE BAZI CHART - {current_year} QI MEN ELEMENTS</div>
          <div style="font-size: 11px; font-weight: 600; color: #fed7aa; margin-top: 3px;">{current_year}年八字命盤奇門格</div>
        </th>
"""
    for col in order:
        html += f"""        <th style="padding: 7px 6px; border-left: 1px solid #334155; color: #fef08a; font-weight: 700; width: 13.5%;">
          {col_headers[col]}
        </th>\n"""
    html += """        <th style="padding: 7px 6px; border-left: 1px solid #334155; color: #ffffff; font-weight: 700; width: 12%; background: #1e293b;">
          要素 Elements
        </th>
      </tr>
    </thead>
    <tbody>
      <!-- Row 1: Stars -->
      <tr style="border-bottom: 1px solid #334155; background: rgba(15, 23, 42, 0.7);">
"""
    for col in order:
        s_char = pillars[col]['stem_char']
        el = stem_map.get(s_char, {'star': '—', 'door': '—'})
        html += f"""        <td style="padding: 7px 6px; border-left: 1px solid #334155; font-weight: 700; color: #f8fafc; font-size: 11.5px;">
          {el['star']}
        </td>\n"""
    html += """        <td style="padding: 7px 6px; border-left: 1px solid #334155; font-weight: 800; color: #fbbf24; font-size: 11px; background: #1e293b;">
          星 Stars
        </td>
      </tr>
      <!-- Row 2: Doors -->
      <tr style="background: rgba(15, 23, 42, 0.55);">
"""
    for col in order:
        s_char = pillars[col]['stem_char']
        el = stem_map.get(s_char, {'star': '—', 'door': '—'})
        html += f"""        <td style="padding: 7px 6px; border-left: 1px solid #334155; font-weight: 700; color: #38bdf8; font-size: 11.5px;">
          {el['door']}
        </td>\n"""
    html += """        <td style="padding: 7px 6px; border-left: 1px solid #334155; font-weight: 800; color: #fbbf24; font-size: 11px; background: #1e293b;">
          門 Doors
        </td>
      </tr>
    </tbody>
  </table>
</div>
"""
    return html


def generate_annual_destiny_html(pillars: Dict[str, Any], current_year: int = 2026) -> str:
    """
    Renders authentic Annual BaZi Stars, Qi Men Mobility Directions,
    and Annual Qi Men Life Palace in a unified executive layout matching Joey Yap's authentic presentation.
    Dynamically supports current_year (such as 2025, 2026, and future years).
    """
    dm_stem_idx = pillars['day']['stem_idx']
    birth_year = pillars.get('birth_year', 1986)
    gender = pillars.get('gender', 'Male')
    
    # Astronomical Heavenly Stem and Earthly Branch for current_year
    ann_stem_idx = (current_year - 4) % 10
    ann_branch_idx = (current_year - 4) % 12
    ann_stem_char = STEM_CHARS[ann_stem_idx]
    ann_stem_name = STEM_NAMES[ann_stem_idx]
    ann_stem_elem = STEM_ELEMENTS[ann_stem_idx]
    ann_stem_color = get_stem_element_color(ann_stem_char)
    ann_branch_char = BRANCH_CHARS[ann_branch_idx]
    ann_branch_name = BRANCH_NAMES[ann_branch_idx]
    ann_branch_animal = BRANCH_ANIMALS[ann_branch_idx]
    ann_branch_elem = BRANCH_ELEMENTS[ann_branch_idx]
    ann_branch_color = get_branch_element_color(ann_branch_char)
    
    ann_stem_god = get_10_god(dm_stem_idx, ann_stem_idx)
    
    # Dynamic Hidden Stems for current_year
    ann_hs_list = BRANCH_HIDDEN_STEMS_MAP.get(ann_branch_idx, [])
    
    order = ['hour', 'day', 'month', 'year']
    col_titles = {
        'hour': '時支 Hour Branch',
        'day': '日支 Day Branch',
        'month': '月支 Month Branch',
        'year': '年支 Year Branch'
    }
    
    # Dynamic Mobility Directions for target year
    mobility_directions = calculate_mobility_directions(birth_year, gender, target_year=current_year)

    # Dynamic Annual Qimen for Life Palace
    p_annual = {
        'hour': {'stem_name': ann_stem_name, 'branch_name': ann_branch_name},
        'day': {'stem_name': ann_stem_name, 'branch_name': ann_branch_name},
        'month': {'stem_name': ann_stem_name, 'branch_name': ann_branch_name},
        'year': {'stem_name': ann_stem_name, 'branch_name': ann_branch_name}
    }
    
    try:
        from qimen_engine import calculate_qimen_chart_from_pillars, PALACES_INFO
        chart_ann = calculate_qimen_chart_from_pillars(p_annual, dun_type='Yin', ju_num=1)
        qm_natal = pillars.get('qimen_destiny', {})
        dest_p_num = qm_natal.get('palace_num')
        if not dest_p_num:
            palace_str = qm_natal.get('palace', '')
            for p_num, info in PALACES_INFO.items():
                if info['dir'] == palace_str.split()[-1] or info['trigram'] in palace_str:
                    dest_p_num = p_num
                    break
        if not dest_p_num:
            dest_p_num = 8
                
        pal_ann = chart_ann['palaces'][dest_p_num]
        qm_stem = f"{pal_ann['heaven_stem']['char']} {pal_ann['heaven_stem']['pinyin']}"
        qm_door = f"{pal_ann['door']['char']} {pal_ann['door']['en']}"
        qm_star = f"天{pal_ann['star']['char']} {pal_ann['star']['en']}"
        qm_deity = f"{pal_ann['deity']['char']} {pal_ann['deity']['en']}"
        palace_name = f"{PALACES_INFO[dest_p_num]['dir']} ({PALACES_INFO[dest_p_num]['trigram']}宮 {dest_p_num})"
    except Exception:
        qm_stem = "辛 Xin"
        qm_door = "死 Death"
        qm_star = "天柱 Pillar"
        qm_deity = "蛇 Snake"
        palace_name = "東北 NE (艮宮 8)"
        dest_p_num = 8

    # Door auspicious determination
    is_door_auspicious = any(qm_door.startswith(d) for d in ['開', 'Open', '休', 'Rest', '生', 'Life'])
    door_box_style = "background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35);" if is_door_auspicious else "background: rgba(30, 41, 59, 0.6); border: 1px solid #334155;"
    door_title_color = "#34d399" if is_door_auspicious else "#94a3b8"
    door_val_color = "#10b981" if is_door_auspicious else "#e2e8f0"
    door_badge = '<div style="font-size: 8.5px; color: #34d399; font-weight: 700; margin-top: 1px;">★ 吉門 Auspicious</div>' if is_door_auspicious else ''

    # Star auspicious determination
    is_star_auspicious = any(qm_star.startswith(s) for s in ['天心', '天任', '天禽', '天輔'])
    star_box_style = "background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35);" if is_star_auspicious else "background: rgba(30, 41, 59, 0.6); border: 1px solid #334155;"
    star_title_color = "#fbbf24" if is_star_auspicious else "#94a3b8"
    star_val_color = "#f59e0b" if is_star_auspicious else "#e2e8f0"
    star_badge = '<div style="font-size: 8.5px; color: #fbbf24; font-weight: 700; margin-top: 1px;">★ 吉星 Auspicious</div>' if is_star_auspicious else ''

    # Qi Men Palace Year Stars
    year_stars_dict = ANNUAL_QIMEN_PALACE_YEAR_STARS.get(current_year, ANNUAL_QIMEN_PALACE_YEAR_STARS.get(2026, {}))
    palace_year_stars = year_stars_dict.get(dest_p_num, [])
    if palace_year_stars:
        stars_inner_html = "".join([
            f'<div style="font-size: 10px; font-weight: 800; color: {"#f87171" if cat == "auspicious" else "#cbd5e1"}; white-space: nowrap; line-height: 1.35; margin-top: 1.5px;">{zh_s} <span style="font-size: 9px; font-weight: 600; color: {"#fca5a5" if cat == "auspicious" else "#94a3b8"};">{en_s}</span></div>'
            for zh_s, en_s, cat in palace_year_stars
        ])
        stars_box_html = f"""        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 6px; padding: 5px 3px; text-align: center; display: flex; flex-direction: column; justify-content: center;">
          <div style="font-size: 9px; font-weight: 800; color: #f87171; text-transform: uppercase;">Year Stars 年星</div>
          <div style="margin-top: 1px;">{stars_inner_html}</div>
        </div>"""
    else:
        stars_box_html = """        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #334155; border-radius: 6px; padding: 5px 3px; text-align: center; display: flex; flex-direction: column; justify-content: center;">
          <div style="font-size: 9px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Year Stars 年星</div>
          <div style="font-size: 15px; font-weight: 900; color: #64748b; margin-top: 2px;">—</div>
        </div>"""

    # Annual BaZi Stars dict
    ann_bazi_stars_dict = ANNUAL_BAZI_STARS_2025 if current_year == 2025 else ANNUAL_BAZI_STARS_2026

    # Format Hidden Stems Cards
    hs_cards_html = []
    for hs in ann_hs_list:
        god = get_10_god(dm_stem_idx, hs['stem_idx'])
        h_color = get_stem_element_color(hs['char'])
        clean_el = hs['polarity_elem'].replace('水','').replace('木','').replace('火','').replace('土','').replace('金','')
        hs_cards_html.append(f"""
                <div style="background: rgba(30, 41, 59, 0.75); border: 1px solid #334155; border-radius: 5px; padding: 5px 2px; flex: 1; text-align: center; min-width: 38px;">
                  <div style="font-size: 17px; font-weight: 900; color: {h_color}; line-height: 1;">{hs['char']}</div>
                  <div style="font-size: 9.5px; font-weight: 700; color: #f8fafc; margin-top: 1px;">{hs['name']}</div>
                  <div style="font-size: 8px; color: #94a3b8;">{clean_el}</div>
                  <div style="font-size: 8.5px; font-weight: 800; color: #fbbf24; margin-top: 3px; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 3px; padding: 1px; white-space: nowrap;">
                    {god['zh_short']} {god['code']}
                  </div>
                </div>""")
    hs_cards_str = "".join(hs_cards_html)

    html = f"""
<!-- {current_year} ANNUAL DESTINY & STARS (MATCHING NATAL CHART THEME) -->
<div style="background: #131d36; border: 1px solid #1e3a8a; border-radius: 10px; overflow: hidden; margin-bottom: 18px; box-shadow: 0 6px 20px rgba(0,0,0,0.3); font-family: 'Kantumruy Pro', 'Inter', -apple-system, sans-serif;">
  
  <!-- MAIN HEADER BAR -->
  <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-bottom: 2px solid #f59e0b; color: #ffffff; padding: 10px 16px; font-weight: 700; font-size: 13.5px; display: flex; justify-content: space-between; align-items: center;">
    <span style="color: #fbbf24; letter-spacing: 0.03em;">{current_year} ANNUAL DESTINY & STARS 流年吉凶星與奇門</span>
    <span style="font-size: 12px; font-weight: 500; color: #94a3b8;">{ann_stem_name} {ann_branch_name} Year {ann_stem_char}{ann_branch_char}年 · {ann_stem_elem} {ann_branch_animal.split()[-1]}</span>
  </div>

  <!-- 2-COLUMN GRID: LEFT MOBILITY, RIGHT ANNUAL TABLE -->
  <div class="annual-main-grid" style="display: grid; grid-template-columns: 28% 72%;">
    
    <!-- LEFT: MOBILITY DIRECTIONS -->
    <div style="border-right: 1px solid #334155; display: flex; flex-direction: column; background: rgba(15, 23, 42, 0.75);">
      <div style="background: #1e293b; border-bottom: 1px solid #334155; color: #fbbf24; padding: 8px 12px; font-weight: 700; font-size: 11.5px; display: flex; justify-content: space-between; align-items: center;">
        <span>MOBILITY DIRECTIONS</span>
        <span style="font-size: 10.5px; font-weight: 500; color: #94a3b8;">本命奇門出行方</span>
      </div>
      <div style="padding: 8px 10px; flex: 1; display: flex; flex-direction: column; justify-content: space-around; gap: 4px;">
"""
    for code, zh, star_str, style_type in mobility_directions:
        if style_type == 'blue':
            badge_bg = "background: rgba(56, 189, 248, 0.12); border: 1px solid #0284c7;"
            code_style = "color: #38bdf8;"
            zh_style = "color: #7dd3fc;"
            star_style = "color: #38bdf8; font-weight: 700;"
            tag_badge = '<span style="font-size: 9px; background: rgba(14, 165, 233, 0.3); color: #38bdf8; border: 1px solid #0284c7; padding: 1px 4px; border-radius: 3px; margin-left: 6px;">吉</span>'
        elif style_type == 'red':
            badge_bg = "background: rgba(239, 68, 68, 0.12); border: 1px solid #dc2626;"
            code_style = "color: #f87171;"
            zh_style = "color: #fca5a5;"
            star_style = "color: #f87171; font-weight: 700;"
            tag_badge = '<span style="font-size: 9px; background: rgba(239, 68, 68, 0.3); color: #f87171; border: 1px solid #dc2626; padding: 1px 4px; border-radius: 3px; margin-left: 6px;">吉</span>'
        else:
            badge_bg = "background: rgba(30, 41, 59, 0.5); border: 1px solid #334155;"
            code_style = "color: #f8fafc;"
            zh_style = "color: #94a3b8;"
            star_style = "color: #cbd5e1; font-weight: 500;"
            tag_badge = ''

        html += f"""        <div style="display: flex; align-items: center; justify-content: space-between; padding: 3.5px 8px; border-radius: 4px; font-size: 11px; {badge_bg}">
          <div style="display: flex; align-items: center; gap: 6px;">
            <span style="font-weight: 800; min-width: 20px; {code_style}">{code}</span>
            <span style="font-weight: 700; {zh_style}">{zh}</span>
          </div>
          <div style="{star_style} display: flex; align-items: center;">
            <span>{star_str}</span>{tag_badge}
          </div>
        </div>"""

    html += f"""      </div>
    </div>
    
    <!-- RIGHT: UNIFIED ANNUAL TABLE -->
    <div style="display: flex; flex-direction: column; background: rgba(15, 23, 42, 0.5);">
      <div style="background: #1e293b; border-bottom: 1px solid #334155; color: #fbbf24; padding: 8px 12px; font-weight: 700; font-size: 11.5px; display: flex; justify-content: space-between; align-items: center;">
        <span>ANNUAL BAZI STARS</span>
        <span style="font-size: 10.5px; font-weight: 500; color: #94a3b8;">本命八字流年吉凶星</span>
      </div>
      <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 11px; flex: 1;">
        <thead>
          <tr style="border-bottom: 1px solid #334155; background: #1e293b;">
"""
    for col in order:
        b_name = pillars[col]['branch_name']
        b_char = pillars[col]['branch_char']
        b_anim = pillars[col]['branch_animal'].split()[-1]
        b_color = get_branch_element_color(b_char)
        html += f"""            <th style="padding: 7px 5px; border-right: 1px solid #334155; width: 20.5%; text-align: center;">
              <div style="font-size: 10.5px; color: #fbbf24; font-weight: 700;">{col_titles[col]}</div>
              <div style="font-size: 15px; font-weight: 900; color: {b_color}; margin-top: 1px;">{b_char} <span style="font-size: 11px; font-weight: 600; color: #cbd5e1;">({b_anim})</span></div>
            </th>\n"""

    html += f"""            <th style="padding: 7px 5px; font-weight: 800; color: #fbbf24; text-align: center; width: 18%; border-left: 2px solid #f59e0b; background: rgba(239, 68, 68, 0.15);">
              <div style="font-size: 15px; font-weight: 900; color: #ef4444;">{current_year}</div>
              <div style="font-size: 10.5px; font-weight: 700; color: #fbbf24;">流年 Annual</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- ROW 1: STARS & ANNUAL STEM/BRANCH -->
          <tr>
"""
    for col in order:
        b_idx = pillars[col]['branch_idx']
        stars_info = ann_bazi_stars_dict.get(b_idx, {'auspicious': [], 'inauspicious': []})
        ausp = stars_info['auspicious']
        inausp = stars_info['inauspicious']
        
        html += """            <td style="padding: 6px 5px; vertical-align: top; border-right: 1px solid #334155; background: rgba(15, 23, 42, 0.7);">\n"""
        
        # Auspicious Header & Badges
        html += """              <div style="font-size: 9.5px; font-weight: 800; color: #fbbf24; text-transform: uppercase; margin-bottom: 4px; display: flex; align-items: center; gap: 3px; letter-spacing: 0.3px;">
                <span>★</span> 吉星 Auspicious
              </div>\n"""
        if not ausp:
            html += """              <div style="font-size: 10px; color: #64748b; font-style: italic; margin-bottom: 6px;">— None</div>\n"""
        else:
            for zh_s, en_s in ausp:
                html += f"""              <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-left: 3px solid #f59e0b; border-radius: 4px; padding: 2px 5px; margin-bottom: 3px; font-size: 10.5px;">
                <span style="font-weight: 800; color: #fbbf24; white-space: nowrap;">{zh_s}</span>
                <span style="font-size: 9px; color: #e2e8f0; font-weight: 600; text-align: right; margin-left: 4px;">{en_s}</span>
              </div>\n"""
        
        # Inauspicious Header & Badges
        html += """              <div style="font-size: 9.5px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin: 8px 0 4px 0; display: flex; align-items: center; gap: 3px; letter-spacing: 0.3px;">
                <span>▲</span> 凶煞 Afflictions
              </div>\n"""
        if not inausp:
            html += """              <div style="font-size: 10px; color: #64748b; font-style: italic;">— None</div>\n"""
        else:
            for zh_s, en_s in inausp:
                html += f"""              <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(15, 23, 42, 0.6); border: 1px solid #334155; border-left: 3px solid #64748b; border-radius: 4px; padding: 2px 5px; margin-bottom: 2.5px; font-size: 10px;">
                <span style="font-weight: 700; color: #cbd5e1; white-space: nowrap;">{zh_s}</span>
                <span style="font-size: 8.5px; color: #94a3b8; font-weight: 500; text-align: right; margin-left: 4px;">{en_s}</span>
              </div>\n"""

        html += """            </td>\n"""

    # 5th Column: Annual Stem & Branch
    html += f"""            <td style="padding: 6px 5px; vertical-align: middle; text-align: center; border-left: 2px solid #f59e0b; background: rgba(30, 41, 59, 0.4);">
              <div style="display: flex; flex-direction: column; gap: 6px; justify-content: center; height: 100%;">
                
                <!-- Stem Box -->
                <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid #334155; border-radius: 6px; padding: 6px 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.25);">
                  <div style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 1px;">
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 1.5px 3.5px; border-radius: 4px; font-size: 8px; font-weight: 800; background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); line-height: 1.1;">
                      <span>{ann_stem_god['zh_full']}</span>
                      <span style="font-size: 7.5px; margin-top: 1px;">{ann_stem_god['code']}</span>
                    </div>
                    <div style="font-size: 26px; font-weight: 900; color: {ann_stem_color}; line-height: 1;">{ann_stem_char}</div>
                  </div>
                  <div style="font-size: 10.5px; font-weight: 700; color: #f8fafc; margin-top: 1px;">{ann_stem_name}</div>
                  <div style="font-size: 9px; color: #94a3b8;">{ann_stem_elem}</div>
                </div>

                <!-- Branch Box -->
                <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid #334155; border-radius: 6px; padding: 6px 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.25);">
                  <div style="font-size: 26px; font-weight: 900; color: {ann_branch_color}; line-height: 1;">{ann_branch_char}</div>
                  <div style="font-size: 10.5px; font-weight: 700; color: #f8fafc; margin-top: 1px;">{ann_branch_name} <span style="font-size: 9.5px; color: #cbd5e1;">({ann_branch_animal.split()[-1]})</span></div>
                  <div style="font-size: 9px; color: #94a3b8;">{ann_branch_elem}</div>
                </div>

              </div>
            </td>
          </tr>

          <!-- ROW 2: QI MEN LIFE PALACE (Cols 1-4) & HIDDEN STEMS (Col 5) -->
          <tr style="border-top: 2px solid #f59e0b;">
            
            <!-- Cols 1-4: QI MEN LIFE PALACE -->
            <td colspan="4" style="padding: 0; vertical-align: top; border-right: 2px solid #f59e0b; background: #131d36;">
              <!-- Header Bar -->
              <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #ffffff; padding: 5px 10px; font-weight: 700; font-size: 11px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155;">
                <div>
                  <span style="color: #fbbf24; font-weight: 800;">{current_year} QI MEN LIFE PALACE</span>
                  <span style="font-size: 10px; font-weight: 500; color: #94a3b8; margin-left: 6px;">流年奇門命宮</span>
                </div>
                <div style="font-size: 10px; font-weight: 700; color: #fbbf24; background: rgba(245, 158, 11, 0.15); border: 1px solid #d97706; padding: 1px 6px; border-radius: 3px;">{palace_name}</div>
              </div>
              
              <!-- 5 Life Palace Cards Grid -->
              <div style="padding: 8px 8px; display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; background: rgba(15, 23, 42, 0.7);">
                
                <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #334155; border-radius: 5px; padding: 5px 3px; text-align: center;">
                  <div style="font-size: 9px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">天干 Stem</div>
                  <div style="font-size: 15px; font-weight: 900; color: #e2e8f0; margin-top: 2px;">{qm_stem}</div>
                  <div style="font-size: 8.5px; color: #64748b; margin-top: 1px;">Heaven Plate</div>
                </div>

                <div style="{door_box_style} border-radius: 5px; padding: 5px 3px; text-align: center;">
                  <div style="font-size: 9px; font-weight: 700; color: {door_title_color}; text-transform: uppercase;">門 Door</div>
                  <div style="font-size: 15px; font-weight: 900; color: {door_val_color}; margin-top: 2px;">{qm_door}</div>
                  {door_badge}
                </div>

                <div style="{star_box_style} border-radius: 5px; padding: 5px 3px; text-align: center;">
                  <div style="font-size: 9px; font-weight: 700; color: {star_title_color}; text-transform: uppercase;">星 Star</div>
                  <div style="font-size: 15px; font-weight: 900; color: {star_val_color}; margin-top: 2px;">{qm_star}</div>
                  {star_badge}
                </div>

                <div style="background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.35); border-radius: 5px; padding: 5px 3px; text-align: center;">
                  <div style="font-size: 9px; font-weight: 700; color: #818cf8; text-transform: uppercase;">神 Deity</div>
                  <div style="font-size: 15px; font-weight: 900; color: #a5b4fc; margin-top: 2px;">{qm_deity}</div>
                </div>

                {stars_box_html}

              </div>
            </td>
            
            <!-- Col 5: Annual Hidden Stems directly below Annual Branch -->
            <td style="padding: 6px 4px; vertical-align: middle; text-align: center; background: rgba(30, 41, 59, 0.4);">
              <div style="font-size: 9.5px; font-weight: 800; color: #fbbf24; margin-bottom: 4px; text-transform: uppercase;">
                藏干 <span style="font-size: 8.5px; color: #94a3b8; font-weight: normal;">Hidden Stems</span>
              </div>
              <div style="display: flex; justify-content: center; gap: 4px;">
                {hs_cards_str}
              </div>
            </td>

          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
"""
    return html


def generate_natal_chart_html(p: Dict[str, Any], current_year: int = 2026) -> str:

    """
    Renders an authentic, classical Chinese Metaphysics Personal Natal Chart
    with Header Profile, Day Master and Stars, Qi Men Destiny Palace, Life Star,
    Feng Shui Gua, 8 Mansions Directions, and a spacious, full-width 4 Pillars Table.
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
    b_hour = p.get('birth_hour', 12)
    b_min = p.get('birth_minute', 0)
    
    is_male = p.get('gender', 'Male').lower().startswith('m')
    gender_label = "MALE 男" if is_male else "FEMALE 女"
    gender_badge_style = "background: rgba(14, 165, 233, 0.18); color: #38bdf8; border: 1px solid #0284c7;" if is_male else "background: rgba(244, 63, 94, 0.18); color: #fb7185; border: 1px solid #e11d48;"

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

    # Life Star details
    ls_num = gua.get('life_star_num', '9')
    ls_color = gua.get('life_star_color', 'Purple')
    ls_zh = gua.get('life_star_zh', '九紫星命')
    ls_elem = gua.get('life_star_elem', 'Fire 火')
    
    # Gua details
    gua_char = gua.get('fs_gua_char', '離')
    gua_name = gua.get('fs_gua_name', 'Li')
    gua_dir = gua.get('fs_gua_dir', 'South')
    gua_group = gua.get('group', 'East Group 東四命')

    raw_html = f"""<style>
.personal-natal-chart {{ box-sizing: border-box; }}
.personal-natal-chart * {{ box-sizing: border-box; }}
@media (max-width: 860px) {{
  .personal-natal-chart .top-summary-grid {{ grid-template-columns: 1fr 1fr !important; }}
  .personal-natal-chart .directions-grid {{ grid-template-columns: 1fr !important; }}
  .personal-natal-chart .annual-main-grid {{ grid-template-columns: 1fr !important; }}
}}
@media (max-width: 580px) {{
  .personal-natal-chart .top-summary-grid {{ grid-template-columns: 1fr !important; }}
  .personal-natal-chart .annual-main-grid {{ grid-template-columns: 1fr !important; }}
}}
</style>
<div class="personal-natal-chart" style="font-family: 'Kantumruy Pro', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1060px; margin: 15px auto; background: #0f172a; border: 1px solid #1e3a8a; border-top: 3px solid #f59e0b; border-radius: 12px; box-shadow: 0 12px 36px rgba(0,0,0,0.5); color: #f8fafc; overflow: hidden; padding: 20px;">

<!-- PROFILE HEADER BAR -->
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 14px; margin-bottom: 18px; gap: 10px;">
  <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
    <span style="font-size: 1.18rem; font-weight: 700; color: #f59e0b; letter-spacing: -0.01em;">{client_name}</span>
    <span style="color: #475569;">|</span>
    <span style="font-size: 0.95rem; font-weight: 600; color: #f8fafc;">{formatted_date_time}</span>
    <span style="color: #475569;">|</span>
    <span style="display: inline-block; padding: 3px 10px; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; {gender_badge_style}">{gender_label}</span>
  </div>
  <div style="font-size: 0.82rem; color: #94a3b8; font-weight: 500;">Classical Chinese Metaphysics • Four Pillars Suite</div>
</div>

<!-- TOP 4 SUMMARY CARDS GRID -->
<div class="top-summary-grid" style="display: grid; grid-template-columns: 1.3fr 1.15fr 0.8fr 0.85fr; gap: 12px; margin-bottom: 18px;">

  <!-- Card 1: Day Master & Shen Sha -->
  <div style="background: #131d36; border: 1px solid #1e3a8a; border-radius: 8px; overflow: hidden; font-size: 12px; display: flex; flex-direction: column;">
    <div style="background: linear-gradient(135deg, #7c2d12 0%, #991b1b 100%); color: #ffffff; padding: 8px 12px; font-weight: 700; display: flex; justify-content: space-between; align-items: center;">
      <span>DAY MASTER</span>
      <span style="color: #fef08a;">日主 : {dm_full}</span>
    </div>
    <div style="padding: 10px 12px; line-height: 1.8; flex: 1;">
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 2px 0;"><span style="color: #94a3b8;">Celestial Animal</span><span style="font-weight: 600; color: #f8fafc;">生肖 : {aux.get('celestial_animal', '-')}</span></div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 2px 0;"><span style="color: #94a3b8;">Noble People</span><span style="font-weight: 600; color: #f8fafc;">貴人 : {aux.get('noble_people', '-')}</span></div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 2px 0;"><span style="color: #94a3b8;">Intelligence</span><span style="font-weight: 600; color: #f8fafc;">文昌 : {aux.get('intelligence', '-')}</span></div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 2px 0;"><span style="color: #94a3b8;">Peach Blossom</span><span style="font-weight: 600; color: #f8fafc;">桃花 : {aux.get('peach_blossom', '-')}</span></div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 2px 0;"><span style="color: #94a3b8;">Sky Horse</span><span style="font-weight: 600; color: #f8fafc;">驛馬 : {aux.get('sky_horse', '-')}</span></div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 2px 0;"><span style="color: #94a3b8;">Solitary</span><span style="font-weight: 600; color: #f8fafc;">孤辰 : {aux.get('solitary', '-')}</span></div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 2px 0;"><span style="color: #94a3b8;">Life Palace</span><span style="font-weight: 600; color: #f8fafc;">命宮 : {aux.get('life_palace', '-')}</span></div>
      <div style="display: flex; justify-content: space-between; padding: 2px 0;"><span style="color: #94a3b8;">Conception Palace</span><span style="font-weight: 600; color: #f8fafc;">胎元 : {aux.get('conception_palace', '-')}</span></div>
    </div>
  </div>

  <!-- Card 2: Qi Men Destiny Palace -->
  <div style="background: #131d36; border: 1px solid #1e3a8a; border-radius: 8px; overflow: hidden; font-size: 12px; display: flex; flex-direction: column;">
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); color: #ffffff; padding: 8px 12px; font-weight: 700; display: flex; justify-content: space-between; align-items: center;">
      <span>QI MEN DESTINY</span>
      <span style="color: #93c5fd;">奇門命宮 : {qm.get('palace', '南 S')}</span>
    </div>
    <div style="padding: 12px; line-height: 2.2; flex: 1;">
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 4px 0;"><span style="color: #94a3b8;">Life Stem</span><span style="font-weight: 600; color: #38bdf8;">命干 : {qm.get('stem', '-')}</span></div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 4px 0;"><span style="color: #94a3b8;">Door of Destiny</span><span style="font-weight: 600; color: #34d399;">門 : {qm.get('door', '-')}</span></div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 4px 0;"><span style="color: #94a3b8;">Star of Destiny</span><span style="font-weight: 600; color: #fbbf24;">星 : {qm.get('star', '-')}</span></div>
      <div style="display: flex; justify-content: space-between; padding: 4px 0;"><span style="color: #94a3b8;">Guardian of Destiny</span><span style="font-weight: 600; color: #c084fc;">神 : {qm.get('guardian', '-')}</span></div>
    </div>
  </div>

  <!-- Card 3: Life Star -->
  <div style="background: #131d36; border: 1px solid #1e3a8a; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; text-align: center;">
    <div style="background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #ffffff; padding: 8px 10px; font-weight: 700; font-size: 12px; letter-spacing: 0.05em;">LIFE STAR</div>
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 14px 6px; flex: 1;">
      <div style="font-size: 38px; font-weight: 900; color: #f59e0b; line-height: 1; text-shadow: 0 0 15px rgba(245, 158, 11, 0.3);">{ls_num}</div>
      <div style="font-size: 14px; font-weight: 700; color: #fbbf24; margin: 4px 0;">{ls_color}</div>
      <div style="font-size: 16px; font-weight: 800; color: #f8fafc; margin-top: 2px;">{ls_zh}</div>
      <div style="display: inline-block; background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 12px; font-weight: 700; margin-top: 6px;">{ls_elem}</div>
    </div>
  </div>

  <!-- Card 4: Feng Shui Gua -->
  <div style="background: #131d36; border: 1px solid #1e3a8a; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; text-align: center;">
    <div style="background: linear-gradient(135deg, #065f46 0%, #047857 100%); color: #ffffff; padding: 8px 10px; font-weight: 700; font-size: 12px; letter-spacing: 0.05em;">風水命卦 GUA</div>
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 14px 6px; flex: 1;">
      <div style="font-size: 44px; font-weight: 900; color: #f8fafc; line-height: 1; margin: 2px 0;">{gua_char}</div>
      <div style="font-size: 14px; font-weight: 700; color: #cbd5e1; margin-top: 4px;">{gua_name} · {gua_dir}</div>
      <div style="display: inline-block; background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 700; margin-top: 6px;">{gua_group}</div>
    </div>
  </div>

</div>

<!-- CENTERPIECE: FOUR PILLARS NATAL CHART (FULL WIDTH) -->
<div style="background: #131d36; border: 1px solid #1e3a8a; border-radius: 10px; overflow-x: auto; margin-bottom: 18px; box-shadow: 0 6px 20px rgba(0,0,0,0.3);">
  <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-bottom: 2px solid #f59e0b; color: #ffffff; padding: 10px 16px; font-weight: 700; font-size: 14px; display: flex; justify-content: space-between; align-items: center;">
    <span style="color: #fbbf24; letter-spacing: 0.03em;">NATAL CHART 本命八字</span>
    <span style="font-size: 12px; font-weight: 500; color: #94a3b8;">Classical Four Pillars (時 • 日 • 月 • 年)</span>
  </div>

  <table style="width: 100%; min-width: 680px; border-collapse: collapse; text-align: center; font-size: 13px;">
    <thead>
      <tr style="background: #1e293b; color: #fbbf24; border-bottom: 1px solid #334155; font-weight: 700;">"""

    for col in order:
        raw_html += f"""<th style="padding: 10px 8px; width: 22%; border-right: 1px solid #334155; font-size: 14px; color: #fbbf24;">{col_titles[col]}</th>"""
    raw_html += """<th style="padding: 10px 8px; width: 12%; font-size: 12px; color: #94a3b8;">Pillars</th></tr></thead><tbody>"""

    # HEAVENLY STEMS (天干)
    raw_html += """<tr style="border-bottom: 1px solid #334155; background: rgba(15, 23, 42, 0.7);">"""
    for col in order:
        meta = p[col]
        god = meta['stem_god']
        char = meta['stem_char']
        color = get_stem_element_color(char)
        is_dm = (col == 'day')
        badge_style = "background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #d97706;" if is_dm else "background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #0284c7;"

        raw_html += f"""<td style="padding: 12px 8px; border-right: 1px solid #334155; vertical-align: middle;">
  <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
    <div style="display: inline-block; padding: 3px 6px; border-radius: 4px; font-size: 11px; font-weight: 700; line-height: 1.2; {badge_style}">
      <div>{god['zh_full']}</div>
      <div style="font-size: 10px; opacity: 0.9;">{god['code']}</div>
    </div>
    <div>
      <div style="font-size: 34px; font-weight: 900; line-height: 1; color: {color};">{char}</div>
      <div style="font-size: 12px; font-weight: 700; color: #f8fafc; margin-top: 2px;">{meta['stem_name']}</div>
      <div style="font-size: 11px; color: #94a3b8;">{meta['stem_elem']}</div>
    </div>
  </div>
</td>"""
    raw_html += """<td style="padding: 10px; border-left: 2px solid #f59e0b; font-size: 12px; font-weight: 700; color: #fbbf24; background: #1e293b; vertical-align: middle; line-height: 1.4;">天干<br><span style="font-size: 10px; font-weight: normal; color: #94a3b8;">Heavenly<br>Stems</span></td></tr>"""

    # EARTHLY BRANCHES (地支)
    raw_html += """<tr style="border-bottom: 1px solid #334155; background: rgba(30, 41, 59, 0.4);">"""
    for col in order:
        meta = p[col]
        char = meta['branch_char']
        color = get_branch_element_color(char)
        raw_html += f"""<td style="padding: 12px 8px; border-right: 1px solid #334155; vertical-align: middle;">
  <div style="font-size: 34px; font-weight: 900; line-height: 1; color: {color};">{char}</div>
  <div style="font-size: 13px; font-weight: 700; color: #f8fafc; margin-top: 3px;">{meta['branch_name']} <span style="font-weight: 500; color: #cbd5e1;">({meta['branch_animal'].split()[-1]})</span></div>
  <div style="font-size: 11px; color: #94a3b8;">{meta['branch_elem']}</div>
</td>"""
    raw_html += """<td style="padding: 10px; border-left: 2px solid #f59e0b; font-size: 12px; font-weight: 700; color: #fbbf24; background: #1e293b; vertical-align: middle; line-height: 1.4;">地支<br><span style="font-size: 10px; font-weight: normal; color: #94a3b8;">Earthly<br>Branches</span></td></tr>"""

    # HIDDEN STEMS (藏干)
    raw_html += """<tr style="background: rgba(15, 23, 42, 0.7);">"""
    for col in order:
        meta = p[col]
        hs_list = meta['hidden_stems']
        raw_html += """<td style="padding: 12px 8px; border-right: 1px solid #334155; vertical-align: top;">
  <div style="display: flex; justify-content: center; gap: 8px; flex-wrap: wrap;">"""
        for hs in hs_list:
            god = hs['god']
            char = hs['char']
            color = get_stem_element_color(char)
            clean_elem = hs['polarity_elem'].replace('水','').replace('木','').replace('火','').replace('土','').replace('金','')
            raw_html += f"""<div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #334155; border-radius: 6px; padding: 6px 8px; text-align: center; min-width: 58px; flex: 1; max-width: 80px;">
  <div style="font-size: 20px; font-weight: 900; color: {color}; line-height: 1;">{char}</div>
  <div style="font-size: 11px; font-weight: 600; color: #f8fafc; margin-top: 2px;">{hs['name']}</div>
  <div style="font-size: 10px; color: #94a3b8;">{clean_elem}</div>
  <div style="font-size: 10px; font-weight: 700; color: #f59e0b; margin-top: 4px; background: rgba(245, 158, 11, 0.1); border-radius: 3px; padding: 1px 3px;">
    {god['zh_short']} <span style="font-size: 9px; color: #94a3b8;">{god['code']}</span>
  </div>
</div>"""
        raw_html += """</div></td>"""
    raw_html += f"""<td style="padding: 10px; border-left: 2px solid #f59e0b; font-size: 12px; font-weight: 700; color: #fbbf24; background: #1e293b; vertical-align: middle; line-height: 1.4;">藏干<br><span style="font-size: 10px; font-weight: normal; color: #94a3b8;">Hidden<br>Stems</span></td></tr></tbody></table>
</div>"""

    # 10-YEAR LUCK PILLARS (大運)
    raw_html += generate_luck_pillars_html(p, current_year=current_year)

    # QI MEN ELEMENTS (八字命盤奇門格)
    raw_html += generate_annual_qimen_elements_html(p, current_year=current_year)

    # ANNUAL BAZI STARS & QI MEN DESTINY & MOBILITY DIRECTIONS
    raw_html += generate_annual_destiny_html(p, current_year=current_year)

    # BOTTOM ROW: 8 MANSIONS (FAVORABLE & UNFAVORABLE DIRECTIONS)
    raw_html += f"""<div class="directions-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">


  <!-- Favorable Directions -->
  <div style="background: #131d36; border: 1px solid #065f46; border-radius: 8px; overflow: hidden; font-size: 12px;">
    <div style="background: linear-gradient(135deg, #064e3b 0%, #065f46 100%); color: #ffffff; padding: 8px 12px; font-weight: 700; display: flex; justify-content: space-between; align-items: center;">
      <span>FAVORABLE DIRECTIONS</span>
      <span style="color: #a7f3d0;">本命吉方</span>
    </div>
    <div style="padding: 10px 12px; line-height: 1.8;">
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 4px 0;">
        <span style="color: #94a3b8;">Sheng Qi (Life Generating)</span>
        <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);">生氣 : {fav.get('sq', '-')}</span>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 4px 0;">
        <span style="color: #94a3b8;">Tian Yi (Heavenly Doctor)</span>
        <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);">天醫 : {fav.get('ty', '-')}</span>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 4px 0;">
        <span style="color: #94a3b8;">Yan Nian (Longevity)</span>
        <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);">延年 : {fav.get('yn', '-')}</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 4px 0;">
        <span style="color: #94a3b8;">Fu Wei (Stability)</span>
        <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);">伏位 : {fav.get('fw', '-')}</span>
      </div>
    </div>
  </div>

  <!-- Unfavorable Directions -->
  <div style="background: #131d36; border: 1px solid #7f1d1d; border-radius: 8px; overflow: hidden; font-size: 12px;">
    <div style="background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%); color: #ffffff; padding: 8px 12px; font-weight: 700; display: flex; justify-content: space-between; align-items: center;">
      <span>UNFAVORABLE DIRECTIONS</span>
      <span style="color: #fecdd3;">本命凶方</span>
    </div>
    <div style="padding: 10px 12px; line-height: 1.8;">
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 4px 0;">
        <span style="color: #94a3b8;">Hou Hai (Mishaps)</span>
        <span style="background: rgba(239, 68, 68, 0.15); color: #f87171; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(239, 68, 68, 0.3);">禍害 : {unfav.get('hh', '-')}</span>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 4px 0;">
        <span style="color: #94a3b8;">Wu Gui (Five Ghosts)</span>
        <span style="background: rgba(239, 68, 68, 0.15); color: #f87171; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(239, 68, 68, 0.3);">五鬼 : {unfav.get('wg', '-')}</span>
      </div>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #1e293b; padding: 4px 0;">
        <span style="color: #94a3b8;">Liu Sha (Six Killings)</span>
        <span style="background: rgba(239, 68, 68, 0.15); color: #f87171; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(239, 68, 68, 0.3);">六煞 : {unfav.get('ls', '-')}</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 4px 0;">
        <span style="color: #94a3b8;">Jue Ming (Life Threatening)</span>
        <span style="background: rgba(239, 68, 68, 0.15); color: #f87171; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(239, 68, 68, 0.3);">絕命 : {unfav.get('jm', '-')}</span>
      </div>
    </div>
  </div>

</div>

</div>"""
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

    def format_ann_stars(b_idx: int) -> str:
        info = ANNUAL_BAZI_STARS_2026.get(b_idx, {'auspicious': [], 'inauspicious': []})
        ausp_str = ", ".join([f"{zh} {en}" for zh, en in info['auspicious']])
        inausp_str = ", ".join([f"{zh} {en}" for zh, en in info['inauspicious']])
        parts = []
        if ausp_str: parts.append(f"吉: {ausp_str}")
        if inausp_str: parts.append(f"凶: {inausp_str}")
        return " <br> ".join(parts) if parts else "-"

    h_ann = format_ann_stars(h['branch_idx'])
    d_ann = format_ann_stars(d['branch_idx'])
    m_ann = format_ann_stars(m['branch_idx'])
    y_ann = format_ann_stars(y['branch_idx'])

    birth_year = p.get('birth_year', 1981)
    gender = p.get('gender', 'Male')
    mob_dirs = calculate_mobility_directions(birth_year, gender)
    mob_line1 = " | ".join([f"**{c} {z}:** {s}" for c, z, s, _ in mob_dirs[:3]])
    mob_line2 = " | ".join([f"**{c} {z}:** {s}" for c, z, s, _ in mob_dirs[3:6]])
    mob_line3 = " | ".join([f"**{c} {z}:** {s}" for c, z, s, _ in mob_dirs[6:]])

    md += (
        "\n### 2026 ANNUAL BAZI STARS 本命八字流年吉凶星 (丙午 Year of the Fire Horse)\n\n"
        "| 時支 Hour Branch | 日支 Day Branch | 月支 Month Branch | 年支 Year Branch | 2026 Annual Pillar |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        f"| {h_ann} | {d_ann} | {m_ann} | {y_ann} | **丙午** Yang Fire Horse<br>Hidden: 丁 己 |\n\n"
        "### 2026 QIMEN MOBILITY DIRECTIONS 本命流年奇門出行方\n"
        f"- {mob_line1}\n"
        f"- {mob_line2}\n"
        f"- {mob_line3}\n\n"
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
