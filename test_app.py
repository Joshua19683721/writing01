#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試腳本：驗證國小生作文練習APP的核心功能
"""

import os
import sys
import sqlite3
import subprocess
import time

def test_database():
    """測試資料庫初始化"""
    print("🔍 正在測試資料庫初始化...")
    
    # 執行資料庫初始化
    try:
        subprocess.run([sys.executable, "db_init.py"], check=True, capture_output=True)
        print("✅ 資料庫初始化成功")
        
        # 檢查資料庫文件是否存在
        if os.path.exists("student_writing.db"):
            print("✅ 資料庫文件創建成功")
            
            # 驗證表結構
            conn = sqlite3.connect("student_writing.db")
            cursor = conn.cursor()
            
            # 檢查表是否存在
            tables = ["writing_rules", "student_resources", "practice_records"]
            for table in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    print(f"✅ 表 {table} 創建成功")
                else:
                    print(f"❌ 表 {table} 創建失敗")
            
            # 檢查數據是否正確插入
            cursor.execute("SELECT COUNT(*) FROM writing_rules")
            rule_count = cursor.fetchone()[0]
            print(f"📊 寫作規則數量：{rule_count}")
            
            cursor.execute("SELECT COUNT(*) FROM student_resources")
            resource_count = cursor.fetchone()[0]
            print(f"📊 資源數量：{resource_count}")
            
            conn.close()
        else:
            print("❌ 資料庫文件創建失敗")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 資料庫初始化失敗：{e}")
        print(f"錯誤輸出：{e.stderr.decode()}")

def test_requirements():
    """檢查依賴套件"""
    print("\n🔍 正在檢查依賴套件...")
    
    requirements = [
        "pyqt6",
        "jieba", 
        "gTTS",
        "speechrecognition",
        "pyaudio",
        "playsound",
        "flask"
    ]
    
    missing = []
    for req in requirements:
        try:
            __import__(req.replace("-", "_"))
            print(f"✅ {req} 已安裝")
        except ImportError:
            missing.append(req)
            print(f"❌ {req} 未安裝")
    
    if missing:
        print(f"\n⚠️ 缺少必要套件：{', '.join(missing)}")
        print("請執行：pip install -r requirements.txt")
    else:
        print("✅ 所有必要套件已安裝完畢")

def test_writing_advisor():
    """測試核心邏輯"""
    print("\n🔍 正在測試核心功能...")
    
    try:
        from writing_advisor import WritingAdvisor
        
        advisor = WritingAdvisor()
        print("✅ WritingAdvisor 初始化成功")
        
        # 測試建議生成
        sentence = "我有一隻寵物"
        suggestions = advisor.generate_suggestions(sentence)
        print(f"\n📝 測試句子：{sentence}")
        print("💡 生成的建議：")
        for i, sug in enumerate(suggestions, 1):
            print(f"   {i}. {sug}")
        
        # 測試評分功能
        full_text = "我有一隻可愛的小狗。它很聰明，會握手和坐下。每天放學回家，它都會搖著尾巴跑來迎接我。我很喜歡我的小狗。"
        score, details = advisor.calculate_score(full_text)
        print(f"\n📊 作文評分測試：")
        print(f"總分：{score:.1f} 分")
        print("分項得分：")
        for category, points in details.items():
            print(f"   {category}：{points:.1f} 分")
        
        advisor.close()
        print("✅ 核心功能測試通過")
        
    except Exception as e:
        print(f"❌ 核心功能測試失敗：{e}")
        import traceback
        traceback.print_exc()

def test_flask_app():
    """測試Web應用"""
    print("\n🔍 正在測試Web應用...")
    
    try:
        import app
        print("✅ Flask應用載入成功")
        
        # 檢查模板文件
        if os.path.exists("templates/index.html"):
            print("✅ 模板文件存在")
        else:
            print("❌ 模板文件不存在")
            
    except Exception as e:
        print(f"❌ Web應用測試失敗：{e}")

def main():
    """主測試函數"""
    print("=" * 60)
    print("🎯 國小生作文練習APP - 功能測試腳本")
    print("=" * 60)
    
    # 切換到正確目錄
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 執行各項測試
    test_requirements()
    test_database()
    test_writing_advisor()
    test_flask_app()
    
    print("\n" + "=" * 60)
    print("📋 測試完成！")
    print("💡 啟動應用：python main.py")
    print("💡 啟動Web服務：python app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()