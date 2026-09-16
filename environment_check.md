# Environment Check

## 專案資訊

- Project：NUTN Campus Chatbot
- Repository：<https://github.com/s11259029/nutn-agent-2026f-teamNN-campus_chatbox>
- Branch：`main`
- 課程：代理式人工智慧工程

## 組員環境驗證

請每位組員在自己的開發環境執行下方指令，填入實際版本並確認登入狀態。

| 學號 | 姓名 | 作業系統 | VS Code | Python | Git | Codex Extension | Codex 登入 | GitHub 存取 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S11259013 | 羅暐媁 | 待填 | 待填 | 待填 | 待填 | 待填 | 待確認 | 待確認 |
| S11259019 | 莊旻芳 | 待填 | 待填 | 待填 | 待填 | 待填 | 待確認 | 待確認 |
| S11259029 | 李安以 | macOS 26.5 | 待確認 | 3.14.4 | 2.50.1 | 待確認 | 待確認 | 已確認 |

> 登入狀態只需填寫「已確認」，不得在此文件記錄帳號密碼、API Key、Token 或其他憑證。

## 驗證指令

```bash
# Python
python --version

# Git
git --version

# pytest
python -m pytest --version

# Repository 與分支狀態
git remote -v
git branch --show-current
git status
```

VS Code 與 Codex Extension 請從介面的 **Help > About** 及 **Extensions** 頁面確認版本；完成 Codex 與 GitHub 登入後，只記錄驗證結果，不記錄任何憑證。

## Git Workflow 驗證

| 步驟 | 狀態 | 工程證據 |
| --- | --- | --- |
| Clone Repository | 已完成 | Repository 已成功下載至本機 |
| 修改 README | 已完成 | 已建立專題簡介、組員、候選問題與 Agent Necessity |
| `git status` | 已完成 | 可辨識目前分支及檔案變更 |
| `git diff` | 已完成 | 已在提交前檢查 README 差異 |
| Commit | 已完成 | 已建立可追蹤的文件提交紀錄 |
| Push | 已完成初次推送 | `main` 已建立；後續修改待網路恢復後推送 |

## Repository 驗證

- [x] 已建立 Team Repository
- [x] 已建立 `main` 分支
- [x] 已建立 README
- [x] README 已列出組員、學號、題目與初步分工
- [x] 已提出三個 NUTN 候選問題
- [x] 已完成 Agent Necessity 初步分析
- [ ] 已將 `teamNN` 改為實際兩位數組別
- [ ] 已將 Repository 名稱改為全小寫 ASCII 與連字號格式
- [ ] 已邀請教師成為 Collaborator
- [ ] 三位組員皆完成環境版本與登入驗證
- [ ] 已安裝並驗證 `pytest`

## 已知問題與後續處理

1. Repository 名稱中的 `teamNN` 尚未替換為實際組別。
2. `campus_chatbox` 應改為使用連字號的 `campus-chatbot`。
3. S11259029 的目前環境尚未偵測到 VS Code、Codex Extension 與 `pytest`，需安裝或人工確認。
4. 其他組員需在各自電腦完成版本、Codex 登入與 GitHub 存取驗證。

## 驗證結論

Team Repository、README 與基本 Git 工作流程已建立。待所有組員補齊工具版本、登入狀態、`pytest` 與 Repository 命名設定後，即完成 Week 1 Environment Verification。
