from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLabel, QComboBox, QListWidget, QListWidgetItem,
                             QTabWidget, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
import os
from gtts import gTTS
import speech_recognition as sr
from playsound import playsound
from writing_advisor import WritingAdvisor
import db_init  # 導入資料庫初始化模組

# 初始化資料庫（首次運行自動建立）
db_init.init_database()

# 語音播放執行緒（避免阻塞介面）
class TTSThread(QThread):
    finished = pyqtSignal()

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.audio_file = "temp_speech.mp3"

    def run(self):
        try:
            # 生成繁體中文語音
            tts = gTTS(text=self.text, lang='zh-TW')
            tts.save(self.audio_file)
            # 播放語音
            playsound(self.audio_file)
        except Exception as e:
            print(f"❌ 語音播放錯誤：{e}")
        finally:
            # 刪除臨時音訊檔
            if os.path.exists(self.audio_file):
                os.remove(self.audio_file)
            self.finished.emit()

# 語音識別執行緒（麥克風輸入轉文字）
class SpeechRecognitionThread(QThread):
    result = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()

    def run(self):
        with sr.Microphone() as source:
            try:
                # 調整麥克風雜訊
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("🎤 正在聆聽...（請說話）")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                # 識別繁體中文（使用Google語音識別）
                text = self.recognizer.recognize_google(audio, language='zh-TW')
                self.result.emit(text)
            except sr.WaitTimeoutError:
                self.result.emit("⚠️ 聆聽超時，請再試一次～")
            except sr.UnknownValueError:
                self.result.emit("⚠️ 無法識別語音，請清晰說話～")
            except Exception as e:
                self.result.emit(f"❌ 語音識別錯誤：{e}")

class WritingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("國小生作文練習APP（繁體中文）")
        self.setGeometry(100, 100, 1100, 750)
        self.advisor = WritingAdvisor()  # 實例化建議生成器
        self.prev_sentence = ""  # 上一句文本（用於銜接建議）
        self.init_ui()

    def init_ui(self):
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. 標題與年級選擇
        header_layout = QHBoxLayout()
        self.title_label = QLabel("📝 國小生作文練習APP - 邊寫邊引導，輕鬆拿高分")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(["3年級", "4年級", "5年級", "6年級"])
        self.grade_combo.setPlaceholderText("選擇年級")
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(QLabel("選擇年級："))
        header_layout.addWidget(self.grade_combo)
        main_layout.addLayout(header_layout)

        # 2. 分頁標籤（作文模式/造句模式/講話轉寫模式）
        self.tab_widget = QTabWidget()
        self.init_composition_tab()    # 作文模式
        self.init_sentence_tab()       # 造句模式
        self.init_speech_tab()         # 講話轉寫模式
        main_layout.addWidget(self.tab_widget)

        # 3. 狀態列
        self.status_label = QLabel("✅ 已就緒 - 選擇模式開始練習吧～")
        main_layout.addWidget(self.status_label)

    def init_composition_tab(self):
        """初始化作文模式分頁"""
        composition_widget = QWidget()
        layout = QVBoxLayout(composition_widget)

        # 題目選擇區域
        topic_layout = QHBoxLayout()
        self.comp_topic_label = QLabel("選擇作文題目：")
        self.comp_topic_combo = QComboBox()
        self.comp_topic_combo.addItems(["我的寵物", "一次有趣的旅行", "我的好朋友", "難忘的一天", "未來的世界", "我的學校", "中秋佳節"])
        self.comp_start_btn = QPushButton("開始寫作")
        self.comp_start_btn.clicked.connect(self.start_composition)

        topic_layout.addWidget(self.comp_topic_label)
        topic_layout.addWidget(self.comp_topic_combo)
        topic_layout.addWidget(self.comp_start_btn)
        layout.addLayout(topic_layout)

        # 寫作與建議區域
        write_suggest_layout = QHBoxLayout()

        # 左側：寫作框
        self.comp_write_edit = QTextEdit()
        self.comp_write_edit.setPlaceholderText("請逐句輸入作文，每句結束按回車或句號...")
        self.comp_write_edit.textChanged.connect(self.check_composition_sentence)
        write_suggest_layout.addWidget(self.comp_write_edit, stretch=2)

        # 右側：建議列表+語音按鈕
        suggest_layout = QVBoxLayout()
        self.comp_suggest_label = QLabel("✨ 推薦優化建議（點擊採納/點喇叭聆聽）")
        self.comp_suggest_list = QListWidget()
        self.comp_suggest_list.itemClicked.connect(self.adopt_composition_suggestion)
        self.comp_play_suggest_btn = QPushButton("🔊 聆聽建議")
        self.comp_play_suggest_btn.clicked.connect(self.play_composition_suggestion)
        self.comp_play_suggest_btn.setEnabled(False)

        suggest_layout.addWidget(self.comp_suggest_label)
        suggest_layout.addWidget(self.comp_suggest_list)
        suggest_layout.addWidget(self.comp_play_suggest_btn)
        write_suggest_layout.addLayout(suggest_layout, stretch=1)

        layout.addLayout(write_suggest_layout)

        # 評分與儲存按鈕
        btn_layout = QHBoxLayout()
        self.comp_score_btn = QPushButton("🏆 完成作文，生成評分")
        self.comp_score_btn.clicked.connect(self.generate_composition_score)
        self.comp_score_btn.setEnabled(False)
        self.comp_save_btn = QPushButton("💾 儲存練習記錄")
        self.comp_save_btn.clicked.connect(self.save_composition_record)
        self.comp_save_btn.setEnabled(False)
        btn_layout.addWidget(self.comp_score_btn)
        btn_layout.addWidget(self.comp_save_btn)
        layout.addLayout(btn_layout)

        # 評分結果
        self.comp_score_label = QLabel("")
        self.comp_score_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        layout.addWidget(self.comp_score_label)

        self.tab_widget.addTab(composition_widget, "📚 作文模式")

    def init_sentence_tab(self):
        """初始化造句模式分頁"""
        sentence_widget = QWidget()
        layout = QVBoxLayout(sentence_widget)

        # 關鍵詞/句式選擇
        input_layout = QHBoxLayout()
        self.sent_keyword_label = QLabel("輸入關鍵詞（如「開心」「秋天」）：")
        self.sent_keyword_edit = QLineEdit()
        self.sent_keyword_edit.setPlaceholderText("請輸入1個關鍵詞...")
        self.sent_type_combo = QComboBox()
        self.sent_type_combo.addItems(["通用造句", "比喻句", "擬人句", "含細節句"])
        self.sent_start_btn = QPushButton("開始造句")
        self.sent_start_btn.clicked.connect(self.start_sentence)
        input_layout.addWidget(self.sent_keyword_label)
        input_layout.addWidget(self.sent_keyword_edit)
        input_layout.addWidget(QLabel("選擇句式："))
        input_layout.addWidget(self.sent_type_combo)
        input_layout.addWidget(self.sent_start_btn)
        layout.addLayout(input_layout)

        # 造句與建議區域
        sent_suggest_layout = QHBoxLayout()

        # 左側：造句框
        self.sent_write_edit = QTextEdit()
        self.sent_write_edit.setPlaceholderText("根據關鍵詞和句式，輸入你的句子...")
        self.sent_write_edit.textChanged.connect(self.check_sentence)
        sent_suggest_layout.addWidget(self.sent_write_edit, stretch=2)

        # 右側：建議列表+語音按鈕
        suggest_layout = QVBoxLayout()
        self.sent_suggest_label = QLabel("✨ 造句優化建議（點擊採納/點喇叭聆聽）")
        self.sent_suggest_list = QListWidget()
        self.sent_suggest_list.itemClicked.connect(self.adopt_sentence_suggestion)
        self.sent_play_suggest_btn = QPushButton("🔊 聆聽建議")
        self.sent_play_suggest_btn.clicked.connect(self.play_sentence_suggestion)
        self.sent_play_suggest_btn.setEnabled(False)

        suggest_layout.addWidget(self.sent_suggest_label)
        suggest_layout.addWidget(self.sent_suggest_list)
        suggest_layout.addWidget(self.sent_play_suggest_btn)
        sent_suggest_layout.addLayout(suggest_layout, stretch=1)

        layout.addLayout(sent_suggest_layout)

        # 評分與驗證按鈕
        btn_layout = QHBoxLayout()
        self.sent_check_btn = QPushButton("✅ 驗證造句是否符合要求")
        self.sent_check_btn.clicked.connect(self.check_sentence_validity)
        self.sent_check_btn.setEnabled(False)
        self.sent_save_btn = QPushButton("💾 儲存造句記錄")
        self.sent_save_btn.clicked.connect(self.save_sentence_record)
        self.sent_save_btn.setEnabled(False)
        btn_layout.addWidget(self.sent_check_btn)
        btn_layout.addWidget(self.sent_save_btn)
        layout.addLayout(btn_layout)

        # 驗證結果
        self.sent_result_label = QLabel("")
        self.sent_result_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        layout.addWidget(self.sent_result_label)

        self.tab_widget.addTab(sentence_widget, "✏️ 造句模式")

    def init_speech_tab(self):
        """初始化講話轉寫模式分頁"""
        speech_widget = QWidget()
        layout = QVBoxLayout(speech_widget)

        # 語音輸入區域
        speech_input_layout = QHBoxLayout()
        self.speech_label = QLabel("語音轉文字（口語轉書面語）：")
        self.speech_start_btn = QPushButton("🎤 開始說話")
        self.speech_start_btn.clicked.connect(self.start_speech_recognition)
        self.speech_stop_btn = QPushButton("⏹️ 停止聆聽")
        self.speech_stop_btn.clicked.connect(self.stop_speech_recognition)
        self.speech_stop_btn.setEnabled(False)
        speech_input_layout.addWidget(self.speech_label)
        speech_input_layout.addWidget(self.speech_start_btn)
        speech_input_layout.addWidget(self.speech_stop_btn)
        layout.addLayout(speech_input_layout)

        # 轉寫與優化區域
        trans_opt_layout = QHBoxLayout()

        # 左側：轉寫結果+編輯框
        self.speech_trans_edit = QTextEdit()
        self.speech_trans_edit.setPlaceholderText("語音轉寫結果將顯示在這裡...")
        trans_opt_layout.addWidget(self.speech_trans_edit, stretch=2)

        # 右側：優化建議+語音按鈕
        suggest_layout = QVBoxLayout()
        self.speech_suggest_label = QLabel("✨ 書面語優化建議（點擊採納/點喇叭聆聽）")
        self.speech_suggest_list = QListWidget()
        self.speech_suggest_list.itemClicked.connect(self.adopt_speech_suggestion)
        self.speech_play_suggest_btn = QPushButton("🔊 聆聽建議")
        self.speech_play_suggest_btn.clicked.connect(self.play_speech_suggestion)
        self.speech_play_suggest_btn.setEnabled(False)

        suggest_layout.addWidget(self.speech_suggest_label)
        suggest_layout.addWidget(self.speech_suggest_list)
        suggest_layout.addWidget(self.speech_play_suggest_btn)
        trans_opt_layout.addLayout(suggest_layout, stretch=1)

        layout.addLayout(trans_opt_layout)

        # 優化與儲存按鈕
        btn_layout = QHBoxLayout()
        self.speech_optimize_btn = QPushButton("📝 生成書面語優化建議")
        self.speech_optimize_btn.clicked.connect(self.generate_speech_optimization)
        self.speech_optimize_btn.setEnabled(False)
        self.speech_save_btn = QPushButton("💾 儲存轉寫記錄")
        self.speech_save_btn.clicked.connect(self.save_speech_record)
        self.speech_save_btn.setEnabled(False)
        btn_layout.addWidget(self.speech_optimize_btn)
        btn_layout.addWidget(self.speech_save_btn)
        layout.addLayout(btn_layout)

        # 狀態提示
        self.speech_status_label = QLabel("ℹ️ 點擊「開始說話」後，請清晰講述（支援30秒內語音）")
        layout.addWidget(self.speech_status_label)

        self.tab_widget.addTab(speech_widget, "🎤 講話轉寫模式")

    # ------------------------------ 作文模式功能 ------------------------------
    def start_composition(self):
        """開始作文練習"""
        self.comp_write_edit.clear()
        self.comp_suggest_list.clear()
        self.comp_score_label.setText("")
        self.prev_sentence = ""
        self.comp_score_btn.setEnabled(True)
        self.comp_save_btn.setEnabled(True)
        self.comp_play_suggest_btn.setEnabled(False)
        self.status_label.setText(f"📝 正在練習作文：{self.comp_topic_combo.currentText()}（{self.grade_combo.currentText()}）")

    def check_composition_sentence(self):
        """檢查作文句子是否結束"""
        text = self.comp_write_edit.toPlainText()
        if text.endswith("\n") or text.endswith("。"):
            current_sentence = text.strip().split("\n")[-1].split("。")[-2] if "。" in text else text.strip().split("\n")[-1]
            if current_sentence and current_sentence != self.prev_sentence and len(current_sentence) >= 2:
                # 生成建議
                grade = self.grade_combo.currentText().replace("年級", "") + "-6年級"
                suggestions = self.advisor.generate_suggestions(current_sentence, self.prev_sentence, grade)
                self.show_composition_suggestions(suggestions)
                self.prev_sentence = current_sentence
                self.comp_play_suggest_btn.setEnabled(True)

    def show_composition_suggestions(self, suggestions):
        """顯示作文建議"""
        self.comp_suggest_list.clear()
        for idx, sug in enumerate(suggestions, 1):
            QListWidgetItem(f"{idx}. {sug}", self.comp_suggest_list)

    def adopt_composition_suggestion(self, item):
        """採納作文建議"""
        suggested_text = item.text().split(". ")[1]
        text = self.comp_write_edit.toPlainText()
        lines = text.strip().split("\n")
        if lines:
            lines[-1] = suggested_text + "。"
            new_text = "\n".join(lines)
            self.comp_write_edit.setPlainText(new_text)
        self.comp_suggest_list.clear()
        self.comp_play_suggest_btn.setEnabled(False)

    def play_composition_suggestion(self):
        """播放作文建議語音"""
        if self.comp_suggest_list.count() == 0:
            self.status_label.setText("⚠️ 沒有可聆聽的建議～")
            return
        # 合併所有建議為一段文字
        suggestions_text = "、".join([item.text().split(". ")[1] for item in self.comp_suggest_list.findItems("", Qt.MatchFlag.MatchAny)])
        self.status_label.setText("🔊 正在播放建議...")
        # 啟動語音播放執行緒
        self.tts_thread = TTSThread(suggestions_text)
        self.tts_thread.finished.connect(lambda: self.status_label.setText("📝 作文建議播放完畢"))
        self.tts_thread.start()

    def generate_composition_score(self):
        """生成作文評分"""
        full_text = self.comp_write_edit.toPlainText()
        if not full_text.strip():
            self.comp_score_label.setText("⚠️ 作文內容不能為空！")
            return
        total_score, detail_scores = self.advisor.calculate_score(full_text)
        # 生成評分報告
        report = f"""
        📝 作文題目：{self.comp_topic_combo.currentText()}
        🎯 總評分：{total_score:.1f} 分（100分制）
        📊 分項得分：
        - 基礎規範（30分）：{detail_scores['基礎規範']:.1f} 分（句子完整性、標點、長度）
        - 表達技巧（25分）：{detail_scores['表達技巧']:.1f} 分（修辭、形容詞運用）
        - 結構邏輯（25分）：{detail_scores['結構邏輯']:.1f} 分（銜接詞、總分總結構）
        - 內容充實（20分）：{detail_scores['內容充實']:.1f} 分（細節、感受描寫）
        💡 改進建議：
        {self.get_improvement_suggestions(detail_scores)}
        """
        self.comp_score_label.setText(report)
        self.status_label.setText(f"🏆 作文評分完成：{total_score:.1f} 分")

    def save_composition_record(self):
        """儲存作文練習記錄"""
        full_text = self.comp_write_edit.toPlainText()
        if not full_text.strip():
            self.status_label.setText("⚠️ 作文內容不能為空，無法儲存！")
            return
        # 獲取採納的建議文本（簡化：取最後一次建議）
        suggested_text = ""
        if self.comp_suggest_list.count() > 0:
            suggested_text = self.comp_suggest_list.item(0).text().split(". ")[1]
        # 計算分數
        total_score, _ = self.advisor.calculate_score(full_text)
        # 儲存到資料庫
        self.advisor.save_practice_record(
            practice_mode="作文模式",
            topic=self.comp_topic_combo.currentText(),
            input_text=full_text,
            suggested_text=suggested_text,
            score=total_score
        )
        self.status_label.setText("💾 作文練習記錄已儲存！")

    # ------------------------------ 造句模式功能 ------------------------------
    def start_sentence(self):
        """開始造句練習"""
        keyword = self.sent_keyword_edit.text().strip()
        sentence_type = self.sent_type_combo.currentText()
        if not keyword:
            self.sent_result_label.setText("⚠️ 請輸入關鍵詞後再開始！")
            return
        self.sent_write_edit.clear()
        self.sent_suggest_list.clear()
        self.sent_result_label.setText("")
        self.sent_check_btn.setEnabled(True)
        self.sent_save_btn.setEnabled(True)
        self.sent_play_suggest_btn.setEnabled(False)
        self.status_label.setText(f"✏️ 正在練習造句：關鍵詞「{keyword}」，句式「{sentence_type}」")

    def check_sentence(self):
        """檢查造句是否輸入完成"""
        text = self.sent_write_edit.toPlainText().strip()
        if text and (text.endswith("。") or text.endswith("！") or text.endswith("？")):
            keyword = self.sent_keyword_edit.text().strip()
            sentence_type = self.sent_type_combo.currentText()
            grade = self.grade_combo.currentText().replace("年級", "") + "-6年級"
            # 生成造句建議
            suggestions = self.advisor.generate_suggestions(text, grade=grade)
            # 根據句式類型過濾建議
            if sentence_type == "比喻句":
                suggestions = [s for s in suggestions if any(word in s for word in self.advisor.resources["比喻詞"])]
            elif sentence_type == "擬人句":
                suggestions = [s for s in suggestions if any(word in s for word in self.advisor.resources["擬人詞"])]
            elif sentence_type == "含細節句":
                suggestions = [s for s in suggestions if any(word in s for word in self.advisor.resources["時間詞"] + self.advisor.resources["地點詞"])]
            # 不足3個建議時補充
            while len(suggestions) < 3:
                suggestions.append(self.generate_random_sentence_suggestion(keyword, sentence_type))
            self.show_sentence_suggestions(suggestions)
            self.sent_play_suggest_btn.setEnabled(True)

    def generate_random_sentence_suggestion(self, keyword, sentence_type):
        """生成隨機造句建議"""
        adj = random.choice(self.advisor.resources["形容詞"])
        metaphor = random.choice(self.advisor.resources["比喻詞"])
        personify = random.choice(self.advisor.resources["擬人詞"])
        time_word = random.choice(self.advisor.resources["時間詞"])
        place_word = random.choice(self.advisor.resources["地點詞"])
        if sentence_type == "比喻句":
            return f"{adj}的{keyword} {metaphor} {random.choice(self.advisor.resources['喻體'])}一樣，真可愛～"
        elif sentence_type == "擬人句":
            return f"{keyword}在{place_word}裡{personify}著，好像在跟我打招呼～"
        elif sentence_type == "含細節句":
            return f"{time_word}，我在{place_word}看到{adj}的{keyword}，心裡真{random.choice(self.advisor.resources['感受詞'])}～"
        else:
            return f"{adj}的{keyword}讓我覺得{random.choice(self.advisor.resources['感受詞'])}，每次看到都很開心～"

    def show_sentence_suggestions(self, suggestions):
        """顯示造句建議"""
        self.sent_suggest_list.clear()
        for idx, sug in enumerate(suggestions, 1):
            QListWidgetItem(f"{idx}. {sug}", self.sent_suggest_list)

    def adopt_sentence_suggestion(self, item):
        """採納造句建議"""
        suggested_text = item.text().split(". ")[1]
        self.sent_write_edit.setPlainText(suggested_text + "。")
        self.sent_suggest_list.clear()
        self.sent_play_suggest_btn.setEnabled(False)

    def play_sentence_suggestion(self):
        """播放造句建議語音"""
        if self.sent_suggest_list.count() == 0:
            self.status_label.setText("⚠️ 沒有可聆聽的建議～")
            return
        suggestions_text = "、".join([item.text().split(". ")[1] for item in self.sent_suggest_list.findItems("", Qt.MatchFlag.MatchAny)])
        self.status_label.setText("🔊 正在播放建議...")
        self.tts_thread = TTSThread(suggestions_text)
        self.tts_thread.finished.connect(lambda: self.status_label.setText("✏️ 造句建議播放完畢"))
        self.tts_thread.start()

    def check_sentence_validity(self):
        """驗證造句是否符合要求"""
        text = self.sent_write_edit.toPlainText().strip()
        keyword = self.sent_keyword_edit.text().strip()
        sentence_type = self.sent_type_combo.currentText()
        if not text:
            self.sent_result_label.setText("⚠️ 請輸入造句後再驗證！")
            return
        # 檢查是否包含關鍵詞
        if keyword not in text:
            self.sent_result_label.setText(f"❌ 造句未包含關鍵詞「{keyword}」，請修改！")
            return
        # 檢查句式是否符合要求
        valid = True
        reason = ""
        if sentence_type == "比喻句" and not any(word in text for word in self.advisor.resources["比喻詞"]):
            valid = False
            reason = "未使用比喻詞（像/好像/彷彿）"
        elif sentence_type == "擬人句" and not any(word in text for word in self.advisor.resources["擬人詞"]):
            valid = False
            reason = "未使用擬人詞（跳舞/唱歌/微笑）"
        elif sentence_type == "含細節句" and not any(word in text for word in self.advisor.resources["時間詞"] + self.advisor.resources["地點詞"]):
            valid = False
            reason = "未包含時間/地點細節"
        # 輸出結果
        if valid:
            self.sent_result_label.setText(f"✅ 造句符合要求！句子完整、生動，給予5顆星🌟🌟🌟🌟🌟")
            self.status_label.setText("✅ 造句驗證通過！")
        else:
            self.sent_result_label.setText(f"❌ 造句不符合「{sentence_type}」要求：{reason}，參考建議修改～")
            self.status_label.setText(f"❌ 造句驗證未通過：{reason}")

    def save_sentence_record(self):
        """儲存造句練習記錄"""
        text = self.sent_write_edit.toPlainText().strip()
        keyword = self.sent_keyword_edit.text().strip()
        if not text or not keyword:
            self.status_label.setText("⚠️ 關鍵詞或造句內容不能為空，無法儲存！")
            return
        # 獲取採納的建議文本
        suggested_text = ""
        if self.sent_suggest_list.count() > 0:
            suggested_text = self.sent_suggest_list.item(0).text().split(". ")[1]
        # 簡化評分：符合要求得100分，否則80分
        total_score = 100 if "✅" in self.sent_result_label.text() else 80
        # 儲存到資料庫
        self.advisor.save_practice_record(
            practice_mode="造句模式",
            topic=f"關鍵詞「{keyword}」-{self.sent_type_combo.currentText()}",
            input_text=text,
            suggested_text=suggested_text,
            score=total_score
        )
        self.status_label.setText("💾 造句練習記錄已儲存！")

    # ------------------------------ 講話轉寫模式功能 ------------------------------
    def start_speech_recognition(self):
        """開始語音識別"""
        self.speech_start_btn.setEnabled(False)
        self.speech_stop_btn.setEnabled(True)
        self.speech_status_label.setText("🎤 正在聆聽...請清晰講話（最多30秒）")
        # 啟動語音識別執行緒
        self.speech_thread = SpeechRecognitionThread()
        self.speech_thread.result.connect(self.on_speech_recognition_result)
        self.speech_thread.finished.connect(self.on_speech_recognition_finished)
        self.speech_thread.start()

    def stop_speech_recognition(self):
        """停止語音識別（簡化：中斷執行緒）"""
        if hasattr(self, 'speech_thread') and self.speech_thread.isRunning():
            self.speech_thread.terminate()
            self.speech_status_label.setText("⏹️ 已手動停止聆聽")
            self.speech_start_btn.setEnabled(True)
            self.speech_stop_btn.setEnabled(False)

    def on_speech_recognition_result(self, text):
        """語音識別結果回調"""
        self.speech_trans_edit.setText(text)
        if "⚠️" not in text and "❌" not in text:
            self.speech_optimize_btn.setEnabled(True)
            self.speech_save_btn.setEnabled(True)
            self.speech_status_label.setText(f"✅ 語音轉寫完成：{text[:20]}...")
        else:
            self.speech_optimize_btn.setEnabled(False)
            self.speech_save_btn.setEnabled(False)
            self.speech_status_label.setText(text)

    def on_speech_recognition_finished(self):
        """語音識別結束回調"""
        self.speech_start_btn.setEnabled(True)
        self.speech_stop_btn.setEnabled(False)

    def generate_speech_optimization(self):
        """生成講話轉寫優化建議（口語轉書面語）"""
        text = self.speech_trans_edit.toPlainText().strip()
        if not text:
            self.speech_status_label.setText("⚠️ 轉寫內容不能為空！")
            return
        # 口語轉書面語規則
        formal_text = text.replace("啦", "了").replace("喔", "哦").replace("呢", "")
        formal_text = formal_text.replace("然後呢", "然後").replace("後來呀", "後來").replace("就是說", "也就是")
        # 生成優化建議
        grade = self.grade_combo.currentText().replace("年級", "") + "-6年級"
        suggestions = self.advisor.generate_suggestions(formal_text, grade=grade)
        # 補充口語轉書面語建議
        suggestions.append(f"書面語優化：{formal_text}（刪除口語助詞，更符合作文要求）")
        self.show_speech_suggestions(suggestions[:3])
        self.speech_play_suggest_btn.setEnabled(True)

    def show_speech_suggestions(self, suggestions):
        """顯示講話轉寫建議"""
        self.speech_suggest_list.clear()
        for idx, sug in enumerate(suggestions, 1):
            QListWidgetItem(f"{idx}. {sug}", self.speech_suggest_list)

    def adopt_speech_suggestion(self, item):
        """採納講話轉寫建議"""
        suggested_text = item.text().split(". ")[1]
        self.speech_trans_edit.setText(suggested_text)
        self.speech_suggest_list.clear()
        self.speech_play_suggest_btn.setEnabled(False)

    def play_speech_suggestion(self):
        """播放講話轉寫建議語音"""
        if self.speech_suggest_list.count() == 0:
            self.speech_status_label.setText("⚠️ 沒有可聆聽的建議～")
            return
        suggestions_text = "、".join([item.text().split(". ")[1] for item in self.speech_suggest_list.findItems("", Qt.MatchFlag.MatchAny)])
        self.speech_status_label.setText("🔊 正在播放建議...")
        self.tts_thread = TTSThread(suggestions_text)
        self.tts_thread.finished.connect(lambda: self.speech_status_label.setText("✅ 轉寫建議播放完畢"))
        self.tts_thread.start()

    def save_speech_record(self):
        """儲存講話轉寫記錄"""
        text = self.speech_trans_edit.toPlainText().strip()
        if not text or "⚠️" in text or "❌" in text:
            self.speech_status_label.setText("⚠️ 轉寫內容無效，無法儲存！")
            return
        # 獲取採納的建議文本
        suggested_text = ""
        if self.speech_suggest_list.count() > 0:
            suggested_text = self.speech_suggest_list.item(0).text().split(". ")[1]
        # 簡化評分：轉寫成功+優化後得90分
        total_score = 90.0
        # 儲存到資料庫
        self.advisor.save_practice_record(
            practice_mode="講話轉寫模式",
            topic="口語轉書面語練習",
            input_text=text,
            suggested_text=suggested_text,
            score=total_score
        )
        self.speech_status_label.setText("💾 講話轉寫記錄已儲存！")

    # ------------------------------ 通用功能 ------------------------------
    def get_improvement_suggestions(self, detail_scores):
        """根據分項得分生成改進建議"""
        suggestions = []
        if detail_scores['基礎規範'] < 20:
            suggestions.append("❌ 注意句子完整性（包含主謂賓），避免過短/過長句子，句末記得加標點～")
        if detail_scores['表達技巧'] < 15:
            suggestions.append("❌ 多使用比喻句、擬人句和形容詞，讓句子更生動有趣哦～")
        if detail_scores['結構邏輯'] < 15:
            suggestions.append("❌ 段落間加入「首先、然後、此外」等銜接詞，開頭總起、結尾總結～")
        if detail_scores['內容充實'] < 10:
            suggestions.append("❌ 補充時間、地點、動作等細節，加入真實感受，讓作文內容更豐富～")
        if not suggestions:
            return "✅ 各項表現優秀！繼續保持，你已經掌握高分作文技巧啦～"
        return "\n".join(suggestions)

    def closeEvent(self, event):
        """關閉視窗時關閉資料庫連接"""
        self.advisor.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WritingApp()
    window.show()
    sys.exit(app.exec())