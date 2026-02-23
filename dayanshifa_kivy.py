# -*- coding: utf-8 -*-
"""
大衍筮法起卦预测程序 - Android版 (Kivy)
使用蓍草模拟周易大衍筮法起卦
"""

import json
import os
import random
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.utils import platform

# 设置窗口背景色为淡蓝色
Window.clearcolor = (0.878, 0.925, 0.961, 1)  # 淡蓝色 #E0ECF5

# 注册中文字体
import os
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'DroidSansFallback.ttf')
if os.path.exists(FONT_PATH):
    LabelBase.register(name='ChineseFont', fn_regular=FONT_PATH)
    DEFAULT_FONT = 'ChineseFont'
else:
    DEFAULT_FONT = None

# 六十四卦数据
HEXAGRAMS = {
    "111111": ("乾", "天"), "000000": ("坤", "地"), "100010": ("屯", "水雷"),
    "010001": ("蒙", "山水"), "111010": ("需", "水天"), "010111": ("讼", "天水"),
    "010000": ("师", "地水"), "000010": ("比", "水地"), "111011": ("小畜", "风天"),
    "110111": ("履", "天泽"), "111000": ("泰", "地天"), "000111": ("否", "天地"),
    "101111": ("同人", "天火"), "111101": ("大有", "火天"), "001000": ("谦", "地山"),
    "000100": ("豫", "雷地"), "100110": ("随", "泽雷"), "011001": ("蛊", "山风"),
    "110000": ("临", "地泽"), "000011": ("观", "风地"), "100101": ("噬嗑", "火雷"),
    "101001": ("贲", "山火"), "000001": ("剥", "山地"), "100000": ("复", "地雷"),
    "100111": ("无妄", "天雷"), "111001": ("大畜", "山天"), "100001": ("颐", "山雷"),
    "011110": ("大过", "泽风"), "010010": ("坎", "水"), "101101": ("离", "火"),
    "001110": ("咸", "泽山"), "011100": ("恒", "雷风"), "001111": ("遁", "天山"),
    "111100": ("大壮", "雷天"), "000101": ("晋", "火地"), "101000": ("明夷", "地火"),
    "101011": ("家人", "风火"), "110101": ("睽", "火泽"), "001010": ("蹇", "水山"),
    "010100": ("解", "雷水"), "110001": ("损", "山泽"), "100011": ("益", "风雷"),
    "111110": ("夬", "泽天"), "011111": ("姤", "天风"), "000110": ("萃", "泽地"),
    "011000": ("升", "地风"), "010110": ("困", "泽水"), "011010": ("井", "水风"),
    "101110": ("革", "泽火"), "011101": ("鼎", "火风"), "100100": ("震", "雷"),
    "001001": ("艮", "山"), "001011": ("渐", "风山"), "110100": ("归妹", "雷泽"),
    "101100": ("丰", "雷火"), "001101": ("旅", "火山"), "011011": ("巽", "风"),
    "110110": ("兑", "泽"), "010011": ("涣", "风水"), "110010": ("节", "水泽"),
    "001100": ("中孚", "风泽"), "110011": ("小过", "雷山"), "010101": ("既济", "水火"),
    "101010": ("未济", "火水"),
}


class DaYanShiFa:
    """大衍筮法核心逻辑类"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置状态"""
        self.total_straws = 50
        self.working_straws = 49
        self.current_yao = 0
        self.current_bian = 0
        self.yao_values = []
        self.bian_remainders = []
        self.step = "init"
        self.left_pile = 0
        self.right_pile = 0
        self.ren_straw = 0
        self.left_remainder = 0
        self.right_remainder = 0
        self.current_straw_count = 49
    
    def get_yao_symbol(self, value, for_original=True):
        """获取爻的符号"""
        if value == 6:
            return "⚋" if for_original else "⚊"
        elif value == 7:
            return "⚊"
        elif value == 8:
            return "⚋"
        elif value == 9:
            return "⚊" if for_original else "⚋"
        return ""
    
    def get_binary(self, value, for_original=True):
        """获取爻的二进制值"""
        if value == 6:
            return "0" if for_original else "1"
        elif value == 7:
            return "1"
        elif value == 8:
            return "0"
        elif value == 9:
            return "1" if for_original else "0"
        return ""
    
    def get_hexagram_info(self, yao_values, for_original=True):
        """根据爻值获取卦象信息"""
        binary = ""
        symbols = []
        for v in yao_values:
            binary += self.get_binary(v, for_original)
            symbols.append(self.get_yao_symbol(v, for_original))
        
        if binary in HEXAGRAMS:
            name, xiang = HEXAGRAMS[binary]
            return {
                "name": name,
                "xiang": xiang,
                "symbols": symbols,
                "binary": binary
            }
        return None
    
    def has_bian_yao(self, yao_values):
        """检查是否有变爻"""
        return any(v in [6, 9] for v in yao_values)


class StrawCanvas(Widget):
    """蓍草画布类 - Kivy版"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.straw_positions = []
        self.divide_straw_positions = []
        self.left_pile_areas = []
        self.right_pile_areas = []
        self.bind(size=self.on_size_change)
    
    def on_size_change(self, *args):
        """尺寸变化时重绘"""
        if self.app.dayan.step != "init":
            self.redraw_current_state()
    
    def redraw_current_state(self):
        """重绘当前状态"""
        pass
    
    def clear_canvas(self):
        """清空画布"""
        self.canvas.clear()
        with self.canvas:
            Color(0.878, 0.925, 0.961, 1)  # 淡蓝色背景
            Rectangle(pos=self.pos, size=self.size)
    
    def draw_initial_straws(self):
        """绘制初始50根蓍草"""
        self.canvas.clear()
        self.straw_positions = []
        
        with self.canvas:
            Color(0.878, 0.925, 0.961, 1)  # 淡蓝色背景
            Rectangle(pos=self.pos, size=self.size)
            
            straw_height = dp(50)
            straw_width = dp(4)
            spacing = dp(10)
            total_width = 50 * spacing
            start_x = (self.width - total_width) / 2
            start_y = self.height / 2 - straw_height / 2
            
            Color(0.545, 0.271, 0.075, 1)  # 棕色
            for i in range(50):
                x = start_x + i * spacing
                Rectangle(pos=(x, start_y), size=(straw_width, straw_height))
                self.straw_positions.append({
                    'x': x,
                    'y': start_y,
                    'width': straw_width,
                    'height': straw_height,
                    'index': i
                })
    
    def draw_taiji_straw(self):
        """绘制太极蓍草"""
        with self.canvas:
            Color(0.855, 0.647, 0.125, 1)  # 金色
            x = self.width / 2 - dp(30)
            y = self.height - dp(30)
            Rectangle(pos=(x, y), size=(dp(60), dp(4)))
            
            Color(0.4, 0.4, 0.4, 1)
    
    def draw_straws_for_divide(self, count):
        """绘制待分堆的蓍草"""
        self.canvas.clear()
        self.divide_straw_positions = []
        
        with self.canvas:
            Color(0.878, 0.925, 0.961, 1)  # 淡蓝色背景
            Rectangle(pos=self.pos, size=self.size)
            
            # 太极
            Color(0.855, 0.647, 0.125, 1)
            x = self.width / 2 - dp(30)
            y = self.height - dp(30)
            Rectangle(pos=(x, y), size=(dp(60), dp(4)))
            
            # 蓍草
            straw_height = dp(45)
            straw_width = dp(3)
            spacing = dp(8)
            total_width = count * spacing
            start_x = (self.width - total_width) / 2
            start_y = self.height / 2 - straw_height / 2
            
            Color(0.545, 0.271, 0.075, 1)
            for i in range(count):
                x = start_x + i * spacing
                Rectangle(pos=(x, start_y), size=(straw_width, straw_height))
                self.divide_straw_positions.append(x + straw_width / 2)
            
            self.divide_start_x = start_x
            self.divide_end_x = start_x + total_width
            self.divide_count = count
    
    def draw_two_piles(self, left_count, right_count):
        """绘制分成两堆的蓍草"""
        self.canvas.clear()
        self.left_pile_areas = []
        self.right_pile_areas = []
        
        with self.canvas:
            Color(0.878, 0.925, 0.961, 1)  # 淡蓝色背景
            Rectangle(pos=self.pos, size=self.size)
            
            # 太极
            Color(0.855, 0.647, 0.125, 1)
            x = self.width / 2 - dp(30)
            y = self.height - dp(30)
            Rectangle(pos=(x, y), size=(dp(60), dp(4)))
            
            straw_height = dp(40)
            straw_width = dp(3)
            spacing = dp(6)
            
            # 左堆
            Color(0.545, 0.271, 0.075, 1)
            left_start_x = dp(20)
            left_start_y = self.height / 2 - straw_height / 2
            for i in range(left_count):
                row = i // 15
                col = i % 15
                x = left_start_x + col * spacing
                y_pos = left_start_y - row * (straw_height + dp(5))
                Rectangle(pos=(x, y_pos), size=(straw_width, straw_height))
                self.left_pile_areas.append({
                    'x': x, 'y': y_pos, 
                    'width': straw_width, 'height': straw_height
                })
            
            # 右堆
            right_start_x = self.width - dp(120)
            for i in range(right_count):
                row = i // 15
                col = i % 15
                x = right_start_x + col * spacing
                y_pos = left_start_y - row * (straw_height + dp(5))
                Rectangle(pos=(x, y_pos), size=(straw_width, straw_height))
                self.right_pile_areas.append({
                    'x': x, 'y': y_pos,
                    'width': straw_width, 'height': straw_height
                })
            
            # 标签
            Color(0.2, 0.2, 0.2, 1)
        
        # 更新标签
        self.app.update_pile_labels(left_count, right_count)
    
    def draw_ren_straw(self):
        """绘制人蓍草"""
        with self.canvas:
            Color(0.804, 0.522, 0.247, 1)
            x = self.width / 2 - dp(25)
            y = self.height / 2 - dp(2)
            Rectangle(pos=(x, y), size=(dp(50), dp(4)))
    
    def highlight_remainder(self, is_left, count, pile_count):
        """高亮余数蓍草"""
        straw_height = dp(40)
        straw_width = dp(3)
        spacing = dp(6)
        
        with self.canvas:
            Color(0.855, 0.647, 0.125, 1)
            
            if is_left:
                left_start_x = dp(20)
                left_start_y = self.height / 2 - straw_height / 2
                start_idx = pile_count - count
                for i in range(start_idx, pile_count):
                    row = i // 15
                    col = i % 15
                    x = left_start_x + col * spacing
                    y_pos = left_start_y - row * (straw_height + dp(5))
                    Rectangle(pos=(x, y_pos), size=(straw_width, straw_height))
            else:
                right_start_x = self.width - dp(120)
                left_start_y = self.height / 2 - straw_height / 2
                start_idx = pile_count - count
                for i in range(start_idx, pile_count):
                    row = i // 15
                    col = i % 15
                    x = right_start_x + col * spacing
                    y_pos = left_start_y - row * (straw_height + dp(5))
                    Rectangle(pos=(x, y_pos), size=(straw_width, straw_height))
    
    def draw_result(self, original_info, changed_info, yao_values):
        """绘制起卦结果"""
        self.canvas.clear()
        
        with self.canvas:
            Color(0.878, 0.925, 0.961, 1)  # 淡蓝色背景
            Rectangle(pos=self.pos, size=self.size)
            
            yao_height = dp(12)
            yao_width = dp(60)
            gap = dp(8)
            spacing = dp(22)
            
            # 本卦位置
            x1 = self.width / 4 - yao_width / 2
            y_start = self.height - dp(100)
            
            for i, symbol in enumerate(reversed(original_info["symbols"])):
                y = y_start - i * spacing
                yao_idx = 5 - i
                is_bian = yao_values[yao_idx] in [6, 9]
                
                if symbol == "⚊":
                    Color(0.769, 0.118, 0.227, 1)
                    Rectangle(pos=(x1, y), size=(yao_width, yao_height))
                else:
                    Color(0.118, 0.565, 1, 1)
                    Rectangle(pos=(x1, y), size=((yao_width - gap) / 2, yao_height))
                    Rectangle(pos=(x1 + (yao_width + gap) / 2, y), 
                            size=((yao_width - gap) / 2, yao_height))
            
            # 之卦位置
            if changed_info:
                x2 = self.width * 3 / 4 - yao_width / 2
                
                for i, symbol in enumerate(reversed(changed_info["symbols"])):
                    y = y_start - i * spacing
                    
                    if symbol == "⚊":
                        Color(0.769, 0.118, 0.227, 1)
                        Rectangle(pos=(x2, y), size=(yao_width, yao_height))
                    else:
                        Color(0.118, 0.565, 1, 1)
                        Rectangle(pos=(x2, y), size=((yao_width - gap) / 2, yao_height))
                        Rectangle(pos=(x2 + (yao_width + gap) / 2, y),
                                size=((yao_width - gap) / 2, yao_height))
    
    def on_touch_down(self, touch):
        """触摸事件处理"""
        if self.collide_point(*touch.pos):
            self.app.handle_canvas_touch(touch)
            return True
        return super().on_touch_down(touch)
    
    def is_in_left_pile(self, x, y):
        """检查是否点击了左堆"""
        for area in self.left_pile_areas:
            if (area['x'] <= x <= area['x'] + area['width'] + dp(10) and
                area['y'] <= y <= area['y'] + area['height']):
                return True
        return x < self.width / 2 and len(self.left_pile_areas) > 0
    
    def is_in_right_pile(self, x, y):
        """检查是否点击了右堆"""
        for area in self.right_pile_areas:
            if (area['x'] <= x <= area['x'] + area['width'] + dp(10) and
                area['y'] <= y <= area['y'] + area['height']):
                return True
        return x > self.width / 2 and len(self.right_pile_areas) > 0


class DaYanApp(App):
    """主应用类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dayan = DaYanShiFa()
        self.is_started = False
        self.history_file = self.get_history_path()
        self.history_data = self.load_history()
        self.current_question = ""
        self.result_original = None
        self.result_changed = None
    
    def get_history_path(self):
        """获取历史文件路径"""
        if platform == 'android':
            from android.storage import app_storage_path
            return os.path.join(app_storage_path(), 'dayan_history.json')
        return 'dayan_history.json'
    
    def build(self):
        """构建UI"""
        self.title = "大衍筮法起卦"
        
        # 字体参数
        font_kwargs = {'font_name': DEFAULT_FONT} if DEFAULT_FONT else {}
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        
        # 顶部输入区
        top_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        
        self.question_input = TextInput(
            hint_text='输入求卦事项',
            multiline=False,
            font_size=sp(16),
            size_hint_x=0.7,
            **font_kwargs
        )
        top_layout.add_widget(self.question_input)
        
        start_btn = Button(
            text='开始',
            font_size=sp(16),
            size_hint_x=0.15,
            on_press=self.start_divination,
            **font_kwargs
        )
        top_layout.add_widget(start_btn)
        
        history_btn = Button(
            text='历史',
            font_size=sp(16),
            size_hint_x=0.15,
            on_press=self.show_history,
            **font_kwargs
        )
        top_layout.add_widget(history_btn)
        
        main_layout.add_widget(top_layout)
        
        # 进度显示
        self.progress_label = Label(
            text='',
            font_size=sp(14),
            size_hint_y=None,
            height=dp(30),
            color=(0.2, 0.3, 0.3, 1),
            **font_kwargs
        )
        main_layout.add_widget(self.progress_label)
        
        # 蓍草画布区
        canvas_container = BoxLayout(size_hint_y=0.5)
        self.straw_canvas = StrawCanvas(self, size_hint=(1, 1))
        canvas_container.add_widget(self.straw_canvas)
        main_layout.add_widget(canvas_container)
        
        # 堆数标签
        self.pile_label = Label(
            text='',
            font_size=sp(14),
            size_hint_y=None,
            height=dp(25),
            color=(0.3, 0.3, 0.3, 1),
            **font_kwargs
        )
        main_layout.add_widget(self.pile_label)
        
        # 提示区
        self.hint_label = Label(
            text='点击"开始"按钮开始起卦',
            font_size=sp(13),
            size_hint_y=None,
            height=dp(60),
            text_size=(Window.width - dp(20), None),
            halign='center',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1),
            **font_kwargs
        )
        self.hint_label.bind(size=self._update_text_size)
        main_layout.add_widget(self.hint_label)
        
        # 结果显示区
        self.result_label = Label(
            text='',
            font_size=sp(14),
            size_hint_y=None,
            height=dp(80),
            color=(0.1, 0.1, 0.1, 1),
            **font_kwargs
        )
        main_layout.add_widget(self.result_label)
        
        # 按钮区
        btn_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        
        self.copy_btn = Button(
            text='复制卦象',
            font_size=sp(14),
            disabled=True,
            on_press=self.copy_result,
            **font_kwargs
        )
        btn_layout.add_widget(self.copy_btn)
        
        self.copy_prompt_btn = Button(
            text='带提示词复制',
            font_size=sp(14),
            disabled=True,
            on_press=self.copy_result_with_prompt,
            **font_kwargs
        )
        btn_layout.add_widget(self.copy_prompt_btn)
        
        main_layout.add_widget(btn_layout)
        
        # 保存字体参数供其他方法使用
        self.font_kwargs = font_kwargs
        
        return main_layout
    
    def _update_text_size(self, instance, value):
        """更新文本大小"""
        instance.text_size = (instance.width, None)
    
    def update_pile_labels(self, left, right):
        """更新堆数标签"""
        self.pile_label.text = f'左堆: {left}根    右堆: {right}根'
    
    def start_divination(self, instance):
        """开始起卦"""
        question = self.question_input.text.strip()
        if not question:
            self.show_popup("提示", "请输入求卦事项")
            return
        
        self.current_question = question
        self.is_started = True
        self.dayan.reset()
        self.result_original = None
        self.result_changed = None
        self.copy_btn.disabled = True
        self.copy_prompt_btn.disabled = True
        self.result_label.text = ''
        self.pile_label.text = ''
        
        # 延迟绘制，确保画布已初始化
        Clock.schedule_once(self._draw_initial, 0.1)
        self.dayan.step = "select_taiji"
    
    def _draw_initial(self, dt):
        """延迟绘制初始蓍草"""
        self.straw_canvas.draw_initial_straws()
        self.update_progress()
        self.hint_label.text = '【第一步：取太极】点击任意一根蓍草取出（共50根，取出1根后剩49根参与演算）'
    
    def update_progress(self):
        """更新进度显示"""
        yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
        bian_names = ["一变", "二变", "三变"]
        
        if self.dayan.current_yao < 6:
            text = f"正在求：{yao_names[self.dayan.current_yao]}"
            if self.dayan.current_bian < 3:
                text += f" {bian_names[self.dayan.current_bian]}"
        else:
            text = "起卦完成"
        
        if self.dayan.yao_values:
            yao_desc = {6: "老阴", 7: "少阳", 8: "少阴", 9: "老阳"}
            vals = [f"{yao_names[i]}:{yao_desc[v]}" for i, v in enumerate(self.dayan.yao_values)]
            text += f"  已得: {', '.join(vals)}"
        
        self.progress_label.text = text
    
    def handle_canvas_touch(self, touch):
        """处理画布触摸"""
        if not self.is_started:
            return
        
        x, y = touch.pos
        
        if self.dayan.step == "select_taiji":
            self.select_taiji_straw(x, y)
        elif self.dayan.step == "divide_piles":
            self.divide_piles(x, y)
        elif self.dayan.step == "take_ren":
            self.take_ren_straw(x, y)
        elif self.dayan.step == "count_left":
            self.count_left_pile(x, y)
        elif self.dayan.step == "count_right":
            self.count_right_pile(x, y)
        elif self.dayan.step == "complete_bian":
            self.complete_bian()
        elif self.dayan.step == "next_yao":
            self.start_next_yao()
    
    def select_taiji_straw(self, x, y):
        """选择太极蓍草"""
        for straw in self.straw_canvas.straw_positions:
            if (straw['x'] <= x <= straw['x'] + straw['width'] + dp(5) and
                straw['y'] <= y <= straw['y'] + straw['height']):
                self.straw_canvas.draw_straws_for_divide(self.dayan.current_straw_count)
                self.dayan.step = "divide_piles"
                self.update_progress()
                self.hint_label.text = '【第二步：分两仪】点击蓍草中间某位置，从该位置将蓍草分成左右两堆'
                return
    
    def divide_piles(self, x, y):
        """分蓍草成两堆"""
        total = self.dayan.current_straw_count
        
        if hasattr(self.straw_canvas, 'divide_straw_positions') and self.straw_canvas.divide_straw_positions:
            positions = self.straw_canvas.divide_straw_positions
            left_count = sum(1 for pos in positions if pos < x)
            
            if left_count < 1:
                left_count = 1
            elif left_count >= total:
                left_count = total - 1
            
            self.dayan.left_pile = left_count
            self.dayan.right_pile = total - left_count
        else:
            self.dayan.left_pile = random.randint(1, total - 1)
            self.dayan.right_pile = total - self.dayan.left_pile
        
        self.straw_canvas.draw_two_piles(self.dayan.left_pile, self.dayan.right_pile)
        self.dayan.step = "take_ren"
        self.update_progress()
        self.hint_label.text = f'已分两仪：左{self.dayan.left_pile}根，右{self.dayan.right_pile}根。【第三步：挂一】点击【右堆】取一根蓍草象征人'
    
    def take_ren_straw(self, x, y):
        """取人蓍草"""
        if not self.straw_canvas.is_in_right_pile(x, y):
            self.hint_label.text = '请点击【右堆】中的一根蓍草取出作为挂一'
            return
        
        self.dayan.right_pile -= 1
        self.dayan.ren_straw = 1
        
        self.straw_canvas.draw_two_piles(self.dayan.left_pile, self.dayan.right_pile)
        self.straw_canvas.draw_ren_straw()
        
        self.dayan.step = "count_left"
        self.update_progress()
        self.hint_label.text = f'已挂一。【第四步：揲四-左】点击【左堆】，对左堆{self.dayan.left_pile}根以4计数求余'
    
    def count_left_pile(self, x, y):
        """数左堆"""
        if not self.straw_canvas.is_in_left_pile(x, y):
            self.hint_label.text = f'请点击【左堆】进行揲四（左堆共{self.dayan.left_pile}根）'
            return
        
        remainder = self.dayan.left_pile % 4
        if remainder == 0:
            remainder = 4
        self.dayan.left_remainder = remainder
        
        self.straw_canvas.highlight_remainder(True, remainder, self.dayan.left_pile)
        
        # 检查右堆是否为0，如果为0则自动跳过右堆揲四
        if self.dayan.right_pile == 0:
            self.dayan.right_remainder = 0
            total_remainder = self.dayan.left_remainder + self.dayan.right_remainder + self.dayan.ren_straw
            self.dayan.bian_remainders.append(total_remainder)
            self.dayan.current_straw_count -= total_remainder
            
            self.dayan.step = "complete_bian"
            bian_num = self.dayan.current_bian + 1
            yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
            yao_name = yao_names[self.dayan.current_yao]
            
            self.update_progress()
            self.hint_label.text = (
                f'左堆{self.dayan.left_pile}÷4余{self.dayan.left_remainder}根，右堆为0根无需揲四 → '
                f'【归奇】左余{self.dayan.left_remainder}+右余0+挂一={total_remainder}根放一旁，'
                f'剩余{self.dayan.current_straw_count}根。点击完成{yao_name}第{bian_num}变'
            )
            return
        
        self.dayan.step = "count_right"
        self.update_progress()
        self.hint_label.text = f'左堆{self.dayan.left_pile}÷4余{remainder}根。【第五步：揲四-右】点击【右堆】，对右堆{self.dayan.right_pile}根以4计数求余'
    
    def count_right_pile(self, x, y):
        """数右堆"""
        if not self.straw_canvas.is_in_right_pile(x, y):
            self.hint_label.text = f'请点击【右堆】进行揲四（右堆共{self.dayan.right_pile}根）'
            return
        
        remainder = self.dayan.right_pile % 4
        if remainder == 0:
            remainder = 4
        self.dayan.right_remainder = remainder
        
        self.straw_canvas.highlight_remainder(False, remainder, self.dayan.right_pile)
        
        total_remainder = self.dayan.left_remainder + self.dayan.right_remainder + self.dayan.ren_straw
        self.dayan.bian_remainders.append(total_remainder)
        self.dayan.current_straw_count -= total_remainder
        
        self.dayan.step = "complete_bian"
        bian_num = self.dayan.current_bian + 1
        yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
        yao_name = yao_names[self.dayan.current_yao]
        
        self.update_progress()
        self.hint_label.text = (
            f'右堆{self.dayan.right_pile}÷4余{self.dayan.right_remainder}根 → '
            f'【归奇】左余{self.dayan.left_remainder}+右余{self.dayan.right_remainder}+挂一={total_remainder}根放一旁，'
            f'剩余{self.dayan.current_straw_count}根。点击完成{yao_name}第{bian_num}变'
        )
    
    def complete_bian(self):
        """完成一变"""
        self.dayan.current_bian += 1
        yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
        
        if self.dayan.current_bian < 3:
            self.dayan.step = "divide_piles"
            bian_num = self.dayan.current_bian + 1
            yao_name = yao_names[self.dayan.current_yao]
            bian_names = ["一变", "二变", "三变"]
            
            self.straw_canvas.draw_straws_for_divide(self.dayan.current_straw_count)
            self.update_progress()
            self.hint_label.text = f'【{yao_name}·{bian_names[self.dayan.current_bian]}】剩余{self.dayan.current_straw_count}根蓍草。点击蓍草中间某位置分两仪'
        else:
            yao_value = self.dayan.current_straw_count // 4
            self.dayan.yao_values.append(yao_value)
            
            yao_desc = {6: "老阴（⚋变⚊）", 7: "少阳（⚊不变）", 8: "少阴（⚋不变）", 9: "老阳（⚊变⚋）"}
            yao_name_result = yao_desc.get(yao_value, "")
            yao_name = yao_names[self.dayan.current_yao]
            
            self.dayan.current_yao += 1
            
            if self.dayan.current_yao < 6:
                self.dayan.current_bian = 0
                self.dayan.bian_remainders = []
                self.dayan.current_straw_count = 49
                self.dayan.step = "next_yao"
                next_yao_name = yao_names[self.dayan.current_yao]
                self.update_progress()
                self.hint_label.text = f'【{yao_name}完成】三变后剩{yao_value * 4}根÷4={yao_value}，得{yao_name_result}。点击开始求【{next_yao_name}】'
            else:
                self.update_progress()
                self.complete_divination()
    
    def start_next_yao(self):
        """开始下一爻"""
        self.dayan.step = "divide_piles"
        yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
        yao_name = yao_names[self.dayan.current_yao]
        
        self.straw_canvas.draw_straws_for_divide(self.dayan.current_straw_count)
        self.update_progress()
        self.hint_label.text = f'【{yao_name}·一变】重新取49根蓍草。点击蓍草中间某位置分两仪'
    
    def complete_divination(self):
        """完成起卦"""
        self.is_started = False
        
        self.result_original = self.dayan.get_hexagram_info(self.dayan.yao_values, True)
        
        if self.dayan.has_bian_yao(self.dayan.yao_values):
            self.result_changed = self.dayan.get_hexagram_info(self.dayan.yao_values, False)
        else:
            self.result_changed = None
        
        self.straw_canvas.draw_result(self.result_original, self.result_changed, self.dayan.yao_values)
        
        # 显示结果文本
        yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
        yao_desc = {6: "老阴", 7: "少阳", 8: "少阴", 9: "老阳"}
        
        result_text = f"本卦：{self.result_original['xiang']}{self.result_original['name']}\n"
        yao_parts = [f"{yao_names[i]}{yao_desc[v]}" for i, v in enumerate(self.dayan.yao_values)]
        result_text += "，".join(yao_parts)
        
        if self.result_changed:
            result_text += f"\n之卦：{self.result_changed['xiang']}{self.result_changed['name']}"
        else:
            result_text += "\n之卦：无"
        
        self.result_label.text = result_text
        self.hint_label.text = '起卦完成！可点击下方按钮复制结果'
        
        self.save_to_history()
        
        self.copy_btn.disabled = False
        self.copy_prompt_btn.disabled = False
    
    def save_to_history(self):
        """保存到历史"""
        record = {
            "question": self.current_question,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "yao_values": self.dayan.yao_values,
            "original_name": self.result_original["name"] if self.result_original else "",
            "original_xiang": self.result_original["xiang"] if self.result_original else "",
            "original_symbols": "".join(self.result_original["symbols"]) if self.result_original else "",
        }
        
        if self.result_changed:
            record["changed_name"] = self.result_changed["name"]
            record["changed_xiang"] = self.result_changed["xiang"]
            record["changed_symbols"] = "".join(self.result_changed["symbols"])
        else:
            record["changed_name"] = ""
            record["changed_xiang"] = ""
            record["changed_symbols"] = ""
        
        self.history_data.append(record)
        self.save_history()
    
    def load_history(self):
        """加载历史"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """保存历史"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")
    
    def show_history(self, instance):
        """显示历史记录"""
        if not self.history_data:
            self.show_popup("提示", "暂无历史记录")
            return
        
        content = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10))
        
        scroll = ScrollView(size_hint=(1, 0.9))
        history_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        history_list.bind(minimum_height=history_list.setter('height'))
        
        for item in sorted(self.history_data, key=lambda x: x.get("date", ""), reverse=True):
            btn = Button(
                text=f"{item.get('question', '未知')} - {item.get('original_name', '')}",
                size_hint_y=None,
                height=dp(40),
                font_size=sp(14),
                **self.font_kwargs
            )
            btn.item = item
            btn.bind(on_press=self.show_history_detail)
            history_list.add_widget(btn)
        
        scroll.add_widget(history_list)
        content.add_widget(scroll)
        
        close_btn = Button(text='关闭', size_hint_y=None, height=dp(40), **self.font_kwargs)
        content.add_widget(close_btn)
        
        popup = Popup(title='历史记录', content=content, size_hint=(0.9, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_history_detail(self, instance):
        """显示历史详情"""
        item = instance.item
        
        detail = f"求卦事项: {item.get('question', '')}\n"
        detail += f"起卦时间: {item.get('date', '')}\n\n"
        detail += f"本卦: {item.get('original_xiang', '')}{item.get('original_name', '')}\n"
        
        if item.get('changed_name'):
            detail += f"之卦: {item.get('changed_xiang', '')}{item.get('changed_name', '')}"
        else:
            detail += "无变卦"
        
        self.show_popup("卦象详情", detail)
    
    def copy_result(self, instance):
        """复制卦象结果"""
        if not self.result_original:
            self.show_popup("提示", "暂无卦象结果可复制")
            return
        
        text = self.result_label.text
        Clipboard.copy(text)
        self.show_popup("提示", "卦象已复制到剪贴板")
    
    def copy_result_with_prompt(self, instance):
        """复制带提示词的卦象结果"""
        if not self.result_original:
            self.show_popup("提示", "暂无卦象结果可复制")
            return
        
        today = datetime.now().strftime("%Y年%m月%d日")
        
        yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "六爻"]
        yao_desc = {6: "老阴", 7: "少阳", 8: "少阴", 9: "老阳"}
        
        original_yao_parts = []
        for i, val in enumerate(self.dayan.yao_values):
            bian_mark = "、动爻" if val in [6, 9] else ""
            original_yao_parts.append(f"{yao_names[i]}{yao_desc[val]}{bian_mark}")
        original_yao_str = "，".join(original_yao_parts)
        
        if self.result_changed:
            changed_yao_parts = []
            for i, val in enumerate(self.dayan.yao_values):
                if val == 6:
                    changed_type = "阳"
                elif val == 9:
                    changed_type = "阴"
                elif val == 7:
                    changed_type = "阳"
                else:
                    changed_type = "阴"
                changed_yao_parts.append(f"{yao_names[i]}{changed_type}")
            changed_yao_str = "，".join(changed_yao_parts)
            
            prompt = f"""你是一名精通周易大衍筮法的中国传统文化预测学专家，某人问{self.current_question}？

于{today}用大衍筮法起卦，得到起卦结果如下

本卦：卦名为{self.result_original['name']}，卦象为{self.result_original['xiang']}，{original_yao_str}。

之卦：卦名为{self.result_changed['name']}，卦象为{self.result_changed['xiang']}，{changed_yao_str}。

然后无需结合现状，仅仅请根据上文起卦得到的文字信息，从卦象阴阳角度，根据大衍筮法的方法，从专家的角度综合进行解卦预测。"""
        else:
            prompt = f"""你是一名精通周易大衍筮法的中国传统文化预测学专家，某人问{self.current_question}？

于{today}用大衍筮法起卦，得到起卦结果如下

本卦：卦名为{self.result_original['name']}，卦象为{self.result_original['xiang']}，{original_yao_str}，无变卦。

然后无需结合现状，仅仅请根据上文起卦得到的文字信息，从卦象阴阳角度，根据大衍筮法的方法，从专家的角度综合进行解卦预测。"""
        
        Clipboard.copy(prompt)
        self.show_popup("提示", "带提示词的卦象已复制到剪贴板")
    
    def show_popup(self, title, message):
        """显示弹窗"""
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, font_size=sp(14), **self.font_kwargs))
        
        close_btn = Button(text='确定', size_hint_y=None, height=dp(40), **self.font_kwargs)
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    DaYanApp().run()
