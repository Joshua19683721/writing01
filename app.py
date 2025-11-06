from flask import Flask, render_template, send_from_directory
import os
import zipfile

app = Flask(__name__)

# 创建ZIP文件的函数
def create_zip():
    zip_filename = 'student_writing_app.zip'
    if not os.path.exists(zip_filename):
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加所有必要的文件
            files_to_zip = [
                'main.py',
                'writing_advisor.py', 
                'db_init.py',
                'requirements_desktop.txt',
                'README.md',
                '.gitignore'
            ]
            
            for file in files_to_zip:
                if os.path.exists(file):
                    zipf.write(file)
        
        print(f"✅ ZIP文件已創建：{zip_filename}")
    return zip_filename

@app.route('/')
def index():
    # 确保ZIP文件存在
    create_zip()
    return render_template('index.html')

@app.route('/download')
def download():
    # 提供ZIP文件下载
    zip_filename = create_zip()
    return send_from_directory('.', zip_filename, as_attachment=True)

@app.route('/files/<path:path>')
def send_file(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    # 创建templates目录（如果不存在）
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 创建index.html文件（如果不存在）
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>國小生作文練習APP</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            max-width: 850px;
            margin: 0 auto;
            padding: 25px;
            line-height: 1.7;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 2.2em;
            font-weight: 700;
        }
        h2 {
            color: #34495e;
            margin: 30px 0 20px;
            font-size: 1.6em;
            font-weight: 600;
        }
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin: 15px 10px;
            font-size: 1.1em;
            font-weight: 600;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        .feature-box {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            margin: 20px 0;
            text-align: left;
            border-left: 5px solid #667eea;
        }
        .feature-item {
            margin: 15px 0;
            font-size: 1.1em;
            display: flex;
            align-items: center;
        }
        .feature-item span {
            margin-right: 15px;
            font-size: 1.3em;
        }
        .installation {
            background: #e8f5e8;
            padding: 25px;
            border-radius: 12px;
            text-align: left;
            margin: 25px 0;
            border: 2px solid #4CAF50;
        }
        .installation h3 {
            color: #2e7d32;
            margin-top: 0;
        }
        .installation ol {
            padding-left: 20px;
        }
        .installation li {
            margin: 10px 0;
        }
        .github-btn {
            background: linear-gradient(135deg, #333 0%, #666 100%);
        }
        .note {
            background: #fff3cd;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #ffeeba;
            text-align: left;
        }
        .note h4 {
            color: #856404;
            margin-top: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 國小生作文練習APP</h1>
        <p style="font-size: 1.2em; color: #666; margin-bottom: 30px;">
            邊寫邊引導，輕鬆拿高分的智能作文練習工具
        </p>
        
        <div style="margin: 40px 0;">
            <a href="/download" class="btn">📥 下載完整套件 (ZIP)</a>
            <a href="https://github.com/Joshua19683721/writing01" target="_blank" class="btn github-btn">
                🌟 查看GitHub原始碼
            </a>
        </div>

        <h2>🚀 主要功能</h2>
        <div class="feature-box">
            <div class="feature-item">
                <span>📚</span>
                <span><strong>作文模式</strong>：選擇題目逐句書寫，即時推送3個優化建議</span>
            </div>
            <div class="feature-item">
                <span>✏️</span>
                <span><strong>造句模式</strong>：輸入關鍵詞+選擇句式，引導擴寫並驗證</span>
            </div>
            <div class="feature-item">
                <span>🎤</span>
                <span><strong>講話轉寫模式</strong>：語音輸入轉文字，自動優化為書面語</span>
            </div>
            <div class="feature-item">
                <span>🔊</span>
                <span><strong>語音朗讀</strong>：建議句繁體中文語音播放，幫助理解流暢度</span>
            </div>
            <div class="feature-item">
                <span>💾</span>
                <span><strong>資料庫儲存</strong>：練習記錄自動保存，包含評分和改進建議</span>
            </div>
            <div class="feature-item">
                <span>🏆</span>
                <span><strong>智能評分</strong>：基於10本寫作規則的多維度評分系統</span>
            </div>
        </div>

        <h2>📋 安裝使用步驟</h2>
        <div class="installation">
            <h3>環境要求：</h3>
            <p style="margin: 10px 0;">• Python 3.8 或更高版本</p>
            <p style="margin: 10px 0;">• Windows 10+/Mac OS 12+/Linux 作業系統</p>
            
            <h3>安裝步驟：</h3>
            <ol>
                <li>下載並解壓 ZIP 套件</li>
                <li>打開終端/命令提示字元，進入套件資料夾</li>
                <li>安裝依賴套件：<code>pip install -r requirements_desktop.txt</code></li>
                <li>啟動應用程式：<code>python main.py</code></li>
            </ol>
        </div>

        <div class="note">
            <h4>⚠️ 注意事項：</h4>
            <p>• 首次啟動會自動初始化資料庫，請稍候片刻</p>
            <p>• 語音功能需要麥克風和喇叭設備</p>
            <p>• 所有數據儲存在本地，保護學生隱私</p>
        </div>

        <h2>🎯 適用對象</h2>
        <p style="font-size: 1.1em; margin: 20px 0;">
            國小3-6年級學生、語文教師、家長輔導使用
        </p>

        <div style="margin: 40px 0; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
            <h2 style="margin-top: 0; color: white;">🌟 為什麼選擇這個APP？</h2>
            <p style="font-size: 1.1em; margin: 15px 0;">
                不同於傳統的作文模板套用，我們的APP採用「即時引導+規則驅動」的方式，
                幫助學生真正掌握寫作技巧，而不是機械抄寫。每個建議都基於學生的實際輸入，
                確保個性化和針對性。
            </p>
        </div>

        <div style="margin-top: 40px; padding-top: 30px; border-top: 2px solid #eee;">
            <p style="color: #666; font-size: 1em;">
                © 2024 國小生作文練習APP | 基於Python + PyQt6開發 | 開源免費
            </p>
        </div>
    </div>
</body>
</html>''')
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
