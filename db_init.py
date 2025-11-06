import sqlite3

def init_database():
    """初始化資料庫：建立規則表、資源表並匯入資料"""
    conn = sqlite3.connect("student_writing.db")
    cursor = conn.cursor()

    # 1. 建立寫作規則表（10本規則核心條目示例）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS writing_rules (
        rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_type TEXT NOT NULL,
        rule_desc TEXT NOT NULL,
        trigger_condition TEXT NOT NULL,
        suggestion_template TEXT NOT NULL,
        score_weight FLOAT NOT NULL,
        grade_range TEXT NOT NULL
    )
    ''')

    # 匯入10本規則核心條目（擴充可補充完整）
    sample_rules = [
        # 基礎規範類（30%權重）
        ("基礎規範", "句子需包含主謂賓，避免殘缺", "句子無謂語", 
         "可以補充【謂語】讓句子更完整～ 比如：【主語】【推薦謂語】【賓語】", 0.1, "3-6年級"),
        ("基礎規範", "避免錯別字（如「的/得/地」混用）", "出現常見錯別字", 
         "這裡可以優化為：【正確表述】，記得【錯別字類型】的用法哦～", 0.1, "3-6年級"),
        ("基礎規範", "句子長度適中（3-6年級建議8-20字）", "句子長度<8字或>20字", 
         "句子可以調整為：【優化後短句】（不長不短，讀起來更順口）", 0.05, "3-6年級"),
        ("基礎規範", "標點符號使用正確（句末用句號）", "句子無句末標點", 
         "記得在句末加句號哦～ 優化後：【句子】。", 0.05, "3-6年級"),
        # 表達技巧類（25%權重）
        ("表達技巧", "適當使用比喻句，讓句子更生動", "連續3句無比喻詞", 
         "可以加入比喻詞（像/好像/彷彿）：【主語】像【喻體】一樣【謂語】", 0.08, "3-6年級"),
        ("表達技巧", "使用具體形容詞，避免籠統表述", "句子無形容詞", 
         "可以加入形容詞：【形容詞】的【主語】【謂語】【賓語】", 0.07, "3-6年級"),
        ("表達技巧", "嘗試擬人句，賦予事物人的動作", "連續3句無擬人詞", 
         "用擬人句試試：【賓語】【擬人詞】著【謂語】，真有趣～", 0.1, "3-6年級"),
        # 結構邏輯類（25%權重）
        ("結構邏輯", "段落銜接需用銜接詞", "上下句關鍵詞相似度<30%", 
         "可以加入銜接詞（首先/然後/此外）：【銜接詞】，【下句優化】", 0.1, "3-6年級"),
        ("結構邏輯", "作文需符合總分總結構", "開頭無總起句", 
         "開頭可以總起：【主題】是我【感受】的一件事，讓我印象深刻", 0.08, "4-6年級"),
        ("結構邏輯", "結尾需總結感受", "結尾無總結句", 
         "結尾可以總結：透過這件事，我明白了【道理】，真是難忘的經歷～", 0.07, "4-6年級"),
        # 內容充實類（20%權重）
        ("內容充實", "加入具體細節（時間/地點/動作）", "句子無細節描寫", 
         "可以補充細節：【時間】，我在【地點】【動作】【賓語】，【感受】", 0.1, "3-6年級"),
        ("內容充實", "描述感受時用具體詞彙", "句子無感受詞", 
         "可以加入感受詞：【主語】【謂語】【賓語】，讓我覺得【感受】極了～", 0.1, "3-6年級")
    ]

    # 先清空表再插入（避免重複）
    cursor.execute("DELETE FROM writing_rules")
    cursor.executemany('''
    INSERT INTO writing_rules (rule_type, rule_desc, trigger_condition, suggestion_template, score_weight, grade_range)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_rules)

    # 2. 建立國小生資源表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student_resources (
        res_id INTEGER PRIMARY KEY AUTOINCREMENT,
        res_type TEXT NOT NULL,
        content TEXT NOT NULL,
        grade_range TEXT NOT NULL
    )
    ''')

    sample_resources = [
        ("比喻詞", "像、好像、彷彿、宛如、猶如、好似", "3-6年級"),
        ("擬人詞", "跳舞、唱歌、微笑、招手、說話、伸懶腰、點頭", "3-6年級"),
        ("銜接詞", "首先、然後、接著、最後、此外、而且、但是、因為、所以", "3-6年級"),
        ("形容詞", "可愛的、開心的、美麗的、有趣的、難忘的、溫柔的、活潑的、圓滾滾的", "3-6年級"),
        ("謂語", "喜歡、愛護、參觀、體驗、分享、陪伴、照顧、玩耍", "3-6年級"),
        ("感受詞", "開心、快樂、興奮、感動、難忘、有趣、滿足、幸福", "3-6年級"),
        ("時間詞", "週末、去年夏天、放學後、國慶節、中秋節、早上、傍晚", "3-6年級"),
        ("地點詞", "公園、動物園、奶奶家、學校、操場、海邊、山頂、圖書館", "3-6年級"),
        ("喻體", "小太陽、棉花糖、小星星、小蜜蜂、花朵、小兔子、小皮球", "3-6年級"),
        ("道理詞", "堅持就是勝利、團結力量大、幫助別人真快樂、認真才能做好事", "4-6年級")
    ]

    # 先清空表再插入
    cursor.execute("DELETE FROM student_resources")
    cursor.executemany('''
    INSERT INTO student_resources (res_type, content, grade_range)
    VALUES (?, ?, ?)
    ''', sample_resources)

    # 3. 建立練習記錄表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS practice_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL DEFAULT 'default_student',
        practice_mode TEXT NOT NULL,
        topic TEXT NOT NULL,
        input_text TEXT NOT NULL,
        suggested_text TEXT,
        score FLOAT NOT NULL DEFAULT 0.0,
        practice_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ 資料庫初始化完成！")

if __name__ == "__main__":
    init_database()