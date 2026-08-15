# 每日心理學知識

每天顯示一則心理學知識的靜態網站。內容來自中文維基百科心理學相關條目,每天由 GitHub Actions 自動挑選一則並更新頁面。

## 運作方式

1. `scripts/build_pool.py` 從 `Category:心理学` 爬取條目摘要,存入 `data/pool.json`(增量合併,不覆蓋既有內容)。
2. `scripts/pick_today.py` 用日期決定當天要顯示池中的哪一則(同一天重跑結果一致,池內容跑完一輪才會重複),寫入 `data/today.json` 並附加到 `data/history.json`。
3. `index.html` / `app.js` 讀取 `data/today.json` 並顯示卡片。
4. `.github/workflows/daily.yml` 每天 UTC 16:00(台北時間 00:00)自動執行上述兩支腳本並將更新的 `data/*.json` commit 回 repo。

## 本機測試

```bash
pip install -r requirements.txt
python scripts/build_pool.py
python scripts/pick_today.py
python -m http.server 8000
# 瀏覽器開啟 http://localhost:8000
```

## 部署到 GitHub Pages

1. 在 GitHub 建立一個新的 public repository,將本專案 push 上去。
2. repo 的 **Settings → Pages**,Source 選擇 `Deploy from a branch`,分支選 `main`,資料夾選 `/ (root)`。
3. 存檔後幾分鐘內會產生網址 `https://<你的帳號>.github.io/<repo名稱>/`。
4. 到 **Actions** 分頁手動觸發一次 `Daily Psychology Knowledge` workflow(`Run workflow`),確認能成功產生並 commit `data/today.json`。
5. 之後每天會自動更新,不需要手動操作。
