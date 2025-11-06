import jieba
import sqlite3
import random

class WritingAdvisor:
    def __init__(self):
        self.conn = sqlite3.connect("student_writing.db")
        self.cursor = self.conn.cursor()
        self.resources = self._load_resources()

    def _load_resources(self):
        """加載國小生常用資源庫"""
        resources = {}
        self.cursor.execute("SELECT res_type, content FROM student_resources WHERE grade_range='3-6年級'")
        for res_type, content in self.cursor.fetchall():
            resources[res_type] = content.split("、")
        return resources

    def _analyze_sentence(self, sentence, prev_sentence=""):
        """分析句子成分和觸發規則"""
        words = jieba.lcut(sentence.strip())
        analysis = {
            "has_subject": False,
            "has_predicate": False,
            "has_object": False,
            "has_rhetoric": False,
            "has_adj": False,
            "has_detail": False,
            "has_feeling": False,
            "sentence_length": len(words),
            "prev_similarity": self._calc_similarity(words, jieba.lcut(prev_sentence.strip()))
        }

        # 定義關鍵詞庫
        subjects = ["我", "你", "他", "她", "它", "我們", "他們", "小明", "小紅", "寵物", "學校", "公園", "媽媽", "爸爸"]
        predicates = self.resources["謂語"]
        objects = ["書", "玩具", "朋友", "風景", "故事", "作業", "寵物", "公園", "禮物", "遊戲"]
        rhetoric_words = self.resources["比喻詞"] + self.resources["擬人詞"]
        adjectives = self.resources["形容詞"]
        detail_words = self.resources["時間詞"] + self.resources["地點詞"]
        feeling_words = self.resources["感受詞"]

        # 匹配關鍵詞
        for word in words:
            if word in subjects:
                analysis["has_subject"] = True
            if word in predicates:
                analysis["has_predicate"] = True
            if word in objects:
                analysis["has_object"] = True
            if word in rhetoric_words:
                analysis["has_rhetoric"] = True
            if word in adjectives:
                analysis["has_adj"] = True
            if word in detail_words:
                analysis["has_detail"] = True
            if word in feeling_words:
                analysis["has_feeling"] = True

        return analysis

    def _calc_similarity(self, words1, words2):
        """計算上下句相似度"""
        if not words1 or not words2:
            return 0.0
        common = set(words1) & set(words2)
        return len(common) / len(set(words1 + words2)) if (words1 + words2) else 0.0

    def generate_suggestions(self, sentence, prev_sentence="", grade="3-6年級"):
        """生成3個個人化優化建議"""
        analysis = self._analyze_sentence(sentence, prev_sentence)
        suggestions = []

        # 匹配觸發規則
        trigger_conditions = []
        if not analysis["has_predicate"]:
            trigger_conditions.append("句子無謂語")
        if not analysis["has_adj"]:
            trigger_conditions.append("句子無形容詞")
        if not analysis["has_rhetoric"]:
            trigger_conditions.append("連續3句無比喻詞")
        if analysis["prev_similarity"] < 0.3:
            trigger_conditions.append("上下句關鍵詞相似度<30%")
        if analysis["sentence_length"] < 8:
            trigger_conditions.append("句子長度<8字")
        if not analysis["has_detail"]:
            trigger_conditions.append("句子無細節描寫")
        if not analysis["has_feeling"]:
            trigger_conditions.append("句子無感受詞")

        # 查詢匹配規則
        if trigger_conditions:
            placeholders = ", ".join(["?"] * len(trigger_conditions))
            self.cursor.execute(f'''
            SELECT rule_type, suggestion_template FROM writing_rules 
            WHERE grade_range=? AND trigger_condition IN ({placeholders})
            ''', (grade,) + tuple(trigger_conditions))
            matched_rules = self.cursor.fetchall()
            random.shuffle(matched_rules)
        else:
            # 無觸發規則時返回通用建議
            self.cursor.execute('''
            SELECT rule_type, suggestion_template FROM writing_rules 
            WHERE grade_range=? LIMIT 3
            ''', (grade,))
            matched_rules = self.cursor.fetchall()

        # 提取句子核心成分
        words = jieba.lcut(sentence)
        subject = next((w for w in words if w in ["我", "你", "他", "寵物", "學校"]), "我")
        object_word = next((w for w in words if w in ["玩具", "朋友", "風景", "寵物"]), "事情")
        predicate = random.choice(self.resources["謂語"])
        adj = random.choice(self.resources["形容詞"])
        metaphor = random.choice(self.resources["比喻詞"])
        connector = random.choice(self.resources["銜接詞"])
        personify = random.choice(self.resources["擬人詞"])
        time_word = random.choice(self.resources["時間詞"])
        place_word = random.choice(self.resources["地點詞"])
        feeling = random.choice(self.resources["感受詞"])
        vehicle = random.choice(self.resources["喻體"])
        truth = random.choice(self.resources["道理詞"])

        # 填充建議模板
        for rule_type, template in matched_rules[:3]:
            suggested = template.replace("【主語】", subject)
            suggested = suggested.replace("【謂語】", predicate)
            suggested = suggested.replace("【推薦謂語】", random.choice(self.resources["謂語"]))
            suggested = suggested.replace("【形容詞】", adj)
            suggested = suggested.replace("【比喻詞】", metaphor)
            suggested = suggested.replace("【銜接詞】", connector)
            suggested = suggested.replace("【賓語】", object_word)
            suggested = suggested.replace("【擬人詞】", personify)
            suggested = suggested.replace("【時間】", time_word)
            suggested = suggested.replace("【地點】", place_word)
            suggested = suggested.replace("【感受】", feeling)
            suggested = suggested.replace("【喻體】", vehicle)
            suggested = suggested.replace("【道理】", truth)
            suggested = suggested.replace("【句子】", sentence.strip())
            suggested = suggested.replace("【主題】", subject + "的" + object_word)
            suggested = suggested.replace("【下句優化】", sentence.strip())
            suggested = suggested.replace("【優化後短句】", adj + "的" + subject + predicate + object_word)
            suggested = suggested.replace("【正確表述】", sentence.strip().replace("的", "得") if "的" in sentence.strip()[-2:] else sentence.strip())
            suggestions.append(suggested)

        # 不足3個建議時補充通用建議
        while len(suggestions) < 3:
            suggestions.append(random.choice([
                f"可以加入細節：{time_word}，{subject}在{place_word} {predicate} {object_word}，{feeling}極了～",
                f"用擬人句試試：{object_word} {personify}著{predicate}，好像在跟我互動呢～",
                f"讓句子更生動：{adj}的{subject} {metaphor} {vehicle}一樣 {predicate}，真有趣～",
                f"加入銜接詞：{connector}，{adj}的{object_word}讓我{feeling}到難以忘懷～"
            ]))

        return suggestions

    def calculate_score(self, full_text):
        """根據10本規則計算總分（100分制）"""
        sentences = [s.strip() for s in full_text.split("。") if s.strip()]
        total_score = 0.0

        # 分項評分（對應規則權重）
        scores = {
            "基礎規範": 30,  # 權重30%
            "表達技巧": 25,  # 權重25%
            "結構邏輯": 25,  # 權重25%
            "內容充實": 20   # 權重20%
        }

        # 1. 基礎規範評分（句子完整性、標點、長度）
        for sent in sentences:
            analysis = self._analyze_sentence(sent)
            if not analysis["has_predicate"]:
                scores["基礎規範"] -= 5
            if analysis["sentence_length"] < 8 or analysis["sentence_length"] > 20:
                scores["基礎規範"] -= 3
            if not sent.endswith(("。", "！", "？")):
                scores["基礎規範"] -= 2
        scores["基礎規範"] = max(scores["基礎規範"], 0)

        # 2. 表達技巧評分（修辭、形容詞）
        rhetoric_count = sum(1 for sent in sentences if self._analyze_sentence(sent)["has_rhetoric"])
        adj_count = sum(1 for sent in sentences if self._analyze_sentence(sent)["has_adj"])
        scores["表達技巧"] = min(25, rhetoric_count * 5 + adj_count * 3)

        # 3. 結構邏輯評分（銜接詞、總分總）
        connector_count = sum(1 for sent in sentences if any(word in self.resources["銜接詞"] for word in jieba.lcut(sent)))
        has_intro = any("是我" in sentences[0] or "讓我" in sentences[0] if sentences else False)
        has_conclusion = any("明白了" in sentences[-1] or "難忘" in sentences[-1] if sentences else False)
        scores["結構邏輯"] = min(25, connector_count * 4 + (5 if has_intro else 0) + (5 if has_conclusion else 0))

        # 4. 內容充實評分（細節、感受）
        detail_count = sum(1 for sent in sentences if self._analyze_sentence(sent)["has_detail"])
        feeling_count = sum(1 for sent in sentences if self._analyze_sentence(sent)["has_feeling"])
        scores["內容充實"] = min(20, detail_count * 3 + feeling_count * 2)

        # 計算總分
        total_score = sum(scores.values())
        return total_score, scores

    def save_practice_record(self, practice_mode, topic, input_text, suggested_text, score):
        """儲存練習記錄到資料庫"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO practice_records (practice_mode, topic, input_text, suggested_text, score)
        VALUES (?, ?, ?, ?, ?)
        ''', (practice_mode, topic, input_text, suggested_text, score))
        self.conn.commit()

    def close(self):
        self.conn.close()