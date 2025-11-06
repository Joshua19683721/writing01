# 部署指南：GitHub + Render

本指南將詳細說明如何將國小生作文練習APP部署到GitHub和Render平台。

## 一、部署到GitHub

### 1. 準備工作
- 確保已安裝Git：https://git-scm.com/downloads
- 擁有GitHub帳號：https://github.com/join

### 2. 建立GitHub儲存庫
1. 登錄GitHub，點擊右上角「+」按鈕，選擇「New repository」；
2. 填寫儲存庫名稱（如 `student-writing-app`）；
3. 選擇「Public」或「Private」（建議Public以便Render訪問）；
4. 勾選「Add a README file」；
5. 點擊「Create repository」。

### 3. 上傳程式碼到GitHub
打開終端/命令提示字元，執行以下步驟：

```bash
# 進入APP資料夾
cd /path/to/student_writing_app

# 初始化Git倉庫
git init

# 新增所有文件
git add .

# 提交變更
git commit -m "Initial commit: 國小生作文練習APP完整版"

# 連接GitHub儲存庫（替換為你的儲存庫URL）
git remote add origin https://github.com/你的GitHub帳號/你的儲存庫名稱.git

# 推送程式碼到GitHub
git push -u origin main
```

### 4. 驗證上傳
打開你的GitHub儲存庫頁面，確認所有文件已成功上傳。

## 二、部署到Render

### 1. 準備工作
- 確保程式碼已上傳到GitHub；
- 擁有Render帳號：https://render.com/（可使用GitHub帳號登錄）。

### 2. 建立Web服務
1. 登錄Render，點擊右上角「New」按鈕，選擇「Web Service」；
2. 在「Connect a repository」頁面，選擇你的GitHub儲存庫；
3. 點擊「Connect」按鈕。

### 3. 配置部署設定
在「Configure your service」頁面，設置以下選項：

- **Name**：輸入服務名稱（如 `student-writing-app`）；
- **Region**：選擇最近的區域（如 `Oregon (US West)`）；
- **Branch**：選擇要部署的分支（通常是 `main`）；
- **Root Directory**：保持預設（留空）；
- **Build Command**：輸入 `pip install -r requirements.txt`；
- **Start Command**：輸入 `python main.py`；

### 4. 高級設定（重要）
點擊「Advanced」展開高級設定：

#### 添加環境變數
點擊「Add Environment Variable」，添加以下變數（如有需要）：
- `PYTHON_VERSION`：設置為 `3.9.7` 或更高版本；
- `PORT`：設置為 `5000`（或其他可用端口）。

#### 設置啟動命令
由於這是一個桌面應用程式，Render可能無法直接運行。我們需要創建一個簡單的Web界面來包裝它。

### 5. 創建Web界面包裝（重要）
由於原始程式是桌面應用程式（基於PyQt6），無法直接在Render上運行。我們需要創建一個簡單的Web界面來提供下載和使用說明。

#### 步驟：
1. 在你的GitHub儲存庫中，創建一個新文件 `app.py`：

```python
from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download():
    # 提供ZIP文件下載
    return send_from_directory('.', 'student_writing_app.zip', as_attachment=True)

@app.route('/files/<path:path>')
def send_file(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
```

2. 創建 `templates/index.html` 文件：

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>國小生作文練習APP</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            text-align: center;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px;
        }
        .btn:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>國小生作文練習APP</h1>
        <p>基於Python開發的作文練習工具，支援作文/造句/講話轉寫三大模式</p>
        
        <h2>📥 下載安裝</h2>
        <a href="/download" class="btn">下載完整套件 (ZIP)</a>
        
        <h2>📋 使用說明</h2>
        <ul style="text-align: left; max-width: 600px; margin: 0 auto;">
            <li>下載並解壓ZIP文件</li>
            <li>安裝Python 3.8+</li>
            <li>執行：pip install -r requirements.txt</li>
            <li>啟動：python main.py</li>
        </ul>
        
        <h2>🌟 主要功能</h2>
        <div style="text-align: left; max-width: 600px; margin: 0 auto;">
            <p>• 📚 作文模式：逐句引導，即時優化建議</p>
            <p>• ✏️ 造句模式：關鍵詞+句式練習</p>
            <p>• 🎤 講話轉寫：語音轉文字，口語轉書面語</p>
            <p>• 🔊 語音朗讀：建議句語音播放</p>
            <p>• 💾 資料庫儲存：練習記錄自動保存</p>
        </div>
        
        <h2>📖 原始碼</h2>
        <a href="https://github.com/你的GitHub帳號/你的儲存庫名稱" target="_blank" class="btn">查看GitHub</a>
    </div>
</body>
</html>
```

3. 更新 `requirements.txt`，添加Flask：

```txt
flask
pyqt6
jieba
gTTS
speechrecognition
pyaudio
playsound==1.2.2
```

4. 重新上傳這些文件到GitHub：

```bash
git add .
git commit -m "Add web interface for Render deployment"
git push
```

### 6. 重新部署到Render
1. 返回Render控制台；
2. 找到你的服務，點擊「Manual Deploy」；
3. 選擇「Deploy latest commit」；
4. 等待部署完成。

### 7. 驗證部署
部署完成後，點擊Render提供的URL，確認Web界面正常運行。

## 三、替代部署方案

### 方案一：僅提供下載服務
如果不需要Web界面，可以將APP打包成可執行文件：

```bash
# 使用PyInstaller打包
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

打包完成後，將生成的可執行文件上傳到GitHub Releases，並在Render上提供下載鏈接。

### 方案二：使用Docker部署
創建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

## 四、常見問題解決

### 1. Render部署失敗
- 檢查Build Command是否正確；
- 確認requirements.txt中的所有套件都可以安裝；
- 檢查環境變數設置。

### 2. 端口佔用問題
- 在Render上使用環境變數PORT；
- 確保應用程式使用正確的端口。

### 3. 靜態文件無法訪問
- 確保文件路徑正確；
- 使用Flask的send_from_directory函數。

## 五、維護與更新

### 1. 更新程式碼
```bash
# 在本地修改程式碼
git add .
git commit -m "Update description"
git push

# 在Render上手動部署或設置自動部署
```

### 2. 監控服務狀態
- 定期檢查Render控制台的服務狀態；
- 設置警報通知。

### 3. 備份數據
- 定期備份GitHub儲存庫；
- 考慮設置自動備份。

---

完成以上步驟後，你的國小生作文練習APP將成功部署到GitHub和Render，用戶可以通過Web界面下載和使用。