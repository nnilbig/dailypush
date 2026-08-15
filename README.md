# 每日心理學知識

每天顯示一則心理學知識的靜態網站。內容取材自 10 位經典心理學家(佛洛伊德、榮格、皮亞傑、斯金納、馬斯洛、羅傑斯、班杜拉、巴夫洛夫、阿德勒、艾瑞克森)的生平與代表理論/概念,每天由 GitHub Actions 自動挑選一則並更新頁面。

## 運作方式

1. `scripts/build_pool.py` 依 `PSYCHOLOGISTS` 清單(10 位心理學家 × 各自的代表理論/概念),逐一在中文維基百科搜尋比對出正確條目並抓摘要,完整寫入 `data/pool.json`(以清單為準,每次執行都會重新產生;之後要增減心理學家或理論,直接改這份清單即可)。
2. `scripts/pick_today.py` 用日期決定當天要顯示池中的哪一則(同一天重跑結果一致,池內容跑完一輪才會重複),寫入 `data/today.json`(含所屬心理學家)並附加到 `data/history.json`。
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
