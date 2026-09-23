# Baseline Declaration 初稿

## 文件資訊

- 專題名稱：NUTN Campus Chatbot
- 本週案例：資工系教師資訊查詢與 Email 草稿產生
- Baseline：`deterministic-fixture-template-v0`
- 文件狀態：初稿（最小 Baseline 已實作）
- 證據狀態：核心函式驗收測試已執行；HTTP API 尚未實作
- 更新日期：2026-09-23

> 本文件為可測試的規格初稿。三個驗收案例與 Known Failure 已使用 Python 核心函式執行；目前尚未建立 HTTP Server，因此測試中的狀態碼為函式回傳的 HTTP-like status，不代表已完成實際 API 請求。

## 1. User Story

> 身為想聯絡資工系教師的學生，我想輸入教師姓名與聯絡目的，讓 Agent 從資工系網站資料查詢教師的研究領域及 Email，並產生合適的郵件草稿，使我能快速、正確且有禮貌地聯絡教師。

## 2. Scope / Out of Scope

### 2.1 In Scope

本週使用固定版本的資工系教師資料，完成以下能力：

- 接收使用者輸入的教師姓名、寄信目的、學生姓名與詢問內容。
- 從固定的資工系教師資料中查詢教師資訊。
- 回傳教師姓名、職稱、研究領域、Email 與資料來源連結。
- 依照寄信目的選擇固定 Email 範本並產生草稿。
- Email 草稿包含收件人、主旨、稱謂、正文、結尾與署名。
- 驗證草稿收件人與固定資料中的教師 Email 完全一致。
- 教師不存在、Email 缺漏或必要欄位不完整時停止處理。
- 使用結構化格式回傳結果，方便自動化測試。
- 僅產生草稿，所有成功結果都必須要求使用者確認。

### 2.2 Out of Scope

本週不包含以下能力：

- 不查詢資工系以外的教師。
- 不即時爬取或更新整個資工系網站。
- 不搜尋固定資料以外的網站或聯絡資訊。
- 不自行猜測不存在或未公開的 Email。
- 不登入 Gmail、Outlook 或學校信箱。
- 不實際寄送 Email。
- 不寄送群組郵件或大量郵件。
- 不加入附件、成績單或其他個人文件。
- 不代表教師回覆或做出任何承諾。
- 不處理付款、簽章或其他具有法律效力的操作。
- 不將郵件草稿視為教師已同意加簽、補交、給分或提供答案。

## 3. 輸入／輸出協定

### 3.1 Endpoint

```http
POST /assistant/email-draft
Content-Type: application/json
```

此 Endpoint 只產生 Email 草稿，不會實際寄出郵件。

### 3.2 Request 必填欄位

| 欄位 | 型別 | 說明 | 驗證規則 |
| --- | --- | --- | --- |
| `teacher_name` | string | 想聯絡的教師姓名 | 去除前後空白後不可為空 |
| `purpose` | string | 寄信目的 | 必須為允許值之一 |
| `student_name` | string | 學生姓名 | 去除前後空白後不可為空 |
| `request_details` | string | 想詢問的具體內容 | 去除前後空白後至少 5 個字 |

### 3.3 Request 選填欄位

| 欄位 | 型別 | 預設值 | 說明 |
| --- | --- | --- | --- |
| `student_id` | string or null | `null` | 學號 |
| `student_department` | string | `"資訊工程學系"` | 學生系所 |
| `student_grade` | string or null | `null` | 年級 |
| `background` | string or null | `null` | 與寄信目的相關的背景 |

`language` 固定為繁體中文，由系統內部設定；測試情境由 fixture 或 mock provider 控制，不放入正式 Request。

### 3.4 `purpose` 允許值

| 值 | 說明 |
| --- | --- |
| `project_inquiry` | 詢問專題名額 |
| `research_inquiry` | 詢問研究方向 |
| `course_question` | 詢問課程問題 |
| `meeting_request` | 預約討論時間 |
| `course_add_request` | 申請課程加簽 |
| `late_submission_request` | 申請補交作業 |
| `answer_request` | 詢問題目答案或解題說明 |
| `grade_inquiry` | 詢問作業、考試或學期分數 |
| `other` | 其他寄信目的 |

當 `purpose` 為 `other` 時，`request_details` 必須清楚說明寄信目的。`answer_request` 只產生詢問解題方向或答案說明的信件，不產生索取未公開考試答案的內容。

### 3.5 Request 範例

```json
{
  "teacher_name": "王小明",
  "purpose": "course_add_request",
  "student_name": "李安以",
  "student_id": "S11259029",
  "student_department": "資訊工程學系",
  "student_grade": "四年級",
  "request_details": "想詢問老師是否可以加簽人工智慧課程",
  "background": "目前仍缺少該領域的必修學分"
}
```

### 3.6 Response 最小可驗證欄位

| 欄位 | 型別 | 說明 |
| --- | --- | --- |
| `can_fulfill` | boolean | 是否能依現有資料產生草稿 |
| `intent` | string | 正規化後的寄信目的 |
| `teacher` | object or null | 經固定資料驗證的教師資訊 |
| `email_draft` | object or null | 郵件收件人、主旨與正文 |
| `sources` | array | 教師資訊的來源 |
| `requires_confirmation` | boolean | 是否需要使用者確認 |
| `send_status` | string | 郵件寄送狀態，本週固定為 `not_sent` |
| `reason` | string | 成功或停止的原因 |
| `error` | object or null | 錯誤代碼與相關欄位 |
| `model_profile` | string | Baseline 類型與版本 |

### 3.7 成功 Response 預期範例

```json
{
  "can_fulfill": true,
  "intent": "course_add_request",
  "teacher": {
    "name": "王小明",
    "title": "教授",
    "email": "wang@example.edu.tw",
    "research_areas": [
      "人工智慧",
      "自然語言處理"
    ],
    "profile_url": "https://example.edu.tw/teachers/wang"
  },
  "email_draft": {
    "to": "wang@example.edu.tw",
    "subject": "人工智慧課程加簽申請",
    "body": "王老師您好：\n\n我是資訊工程學系四年級學生李安以，想詢問是否可以加簽人工智慧課程。\n\n謝謝老師撥冗閱讀。\n\n學生 李安以 敬上"
  },
  "sources": [
    {
      "type": "department_website",
      "url": "https://example.edu.tw/teachers/wang"
    }
  ],
  "requires_confirmation": true,
  "send_status": "not_sent",
  "reason": "已從固定教師資料中找到聯絡資訊並產生郵件草稿。",
  "error": null,
  "model_profile": "deterministic-fixture-template-v0"
}
```

> 上述教師姓名、Email 與網址均為合成測試資料，不代表真實教師資訊。

### 3.8 HTTP 狀態與停止層

| 情況 | HTTP | 停止位置 |
| --- | ---: | --- |
| 成功找到教師並產生草稿 | `200` | 完成輸出 |
| 缺少必要欄位或 `purpose` 不合法 | `422` | Request validation |
| 教師不在固定資料中 | `404` | Teacher lookup |
| 教師存在但沒有公開 Email | `409` | Contact validation |
| 草稿收件人與固定資料不一致 | `502` | Grounding validation |

### 3.9 核心驗證規則

- `email_draft.to` 必須等於固定資料中的 `teacher.email`。
- `teacher.profile_url` 必須來自 fixture 中記錄的資工系網站來源。
- 找不到教師或公開 Email 時，不可自行猜測。
- `email_draft.body` 必須包含學生姓名與寄信目的。
- 所有成功結果的 `requires_confirmation` 必須為 `true`。
- 本週所有結果的 `send_status` 必須為 `not_sent`。

## 4. 三個 Given / When / Then 驗收案例

三個案例使用同一個寄信情境，只改變一個關鍵條件。固定 fixture 包含以下合成資料：

```json
{
  "name": "王小明",
  "title": "教授",
  "email": "wang@example.edu.tw",
  "research_areas": ["人工智慧", "自然語言處理"],
  "profile_url": "https://example.edu.tw/teachers/wang"
}
```

### AC01：正常產生加簽郵件草稿

**Given**

使用者提供完整且合法的輸入，固定資料中存在王小明教授，公開 Email 為 `wang@example.edu.tw`。

```json
{
  "teacher_name": "王小明",
  "purpose": "course_add_request",
  "student_name": "李安以",
  "request_details": "想詢問老師是否可以加簽人工智慧課程"
}
```

**When**

使用者送出 `POST /assistant/email-draft`。

**Then（已執行／通過）**

- 回傳 HTTP `200`。
- `can_fulfill` 為 `true`。
- `teacher.name` 為 `王小明`。
- `email_draft.to` 為 `wang@example.edu.tw`。
- 主旨與正文包含「加簽」或相同意思。
- 正文包含學生姓名「李安以」。
- `requires_confirmation` 為 `true`。
- `send_status` 為 `not_sent`。
- 回傳教師資料來源連結。
- 不實際寄出郵件。

停止層：成功完成輸出。

### AC02：缺少教師姓名

**Given**

使用者提供與 AC01 相同的資料，但 `teacher_name` 為空字串。

```json
{
  "teacher_name": "",
  "purpose": "course_add_request",
  "student_name": "李安以",
  "request_details": "想詢問老師是否可以加簽人工智慧課程"
}
```

**When**

使用者送出 `POST /assistant/email-draft`。

**Then（已執行／通過）**

- Request validation 立即停止處理。
- 回傳 HTTP `422`。
- `can_fulfill` 為 `false`。
- `error.code` 為 `MISSING_REQUIRED_FIELD`。
- `error.missing_fields` 包含 `teacher_name`。
- `teacher` 與 `email_draft` 均為 `null`。
- 不執行教師查詢與郵件草稿產生。
- `send_status` 為 `not_sent`。

停止層：Request validation。

### AC03：草稿 Email 與資料來源不一致

**Given**

使用者提供與 AC01 相同的合法輸入。固定資料中的正確 Email 為 `wang@example.edu.tw`，但內部 ungrounded mock fixture 產生的收件人為 `fake@example.edu.tw`。

**When**

系統驗證 mock provider 的結構化輸出與固定教師資料。

**Then（已執行／通過）**

- Response schema 通過，因為 `fake@example.edu.tw` 的格式合法。
- Grounding validation 發現收件人與固定資料不一致。
- 回傳 HTTP `502`。
- `can_fulfill` 為 `false`。
- `error.code` 為 `UNGROUNDED_EMAIL`。
- 不向使用者提供可使用的郵件草稿。
- `send_status` 為 `not_sent`。
- 錯誤訊息說明 Email 無法通過資料來源驗證。

停止層：Grounding validation。

## 5. Baseline 宣告

### 5.1 類型

本週採用 **Deterministic fixture-backed template**。系統不呼叫真實 LLM，而是使用固定教師 JSON 與依 `purpose` 分類的 Email 範本產生草稿。

### 5.2 執行流程

```text
接收 Request
    ↓
驗證必填欄位
    ↓
從固定 JSON 查詢教師
    ↓
依 purpose 選擇 Email 範本
    ↓
填入教師、學生與詢問內容
    ↓
驗證收件人與教師資料來源一致
    ↓
回傳 Email 草稿
```

### 5.3 選擇理由

- 相同輸入會得到相同輸出，方便重複測試。
- 不需要 API Key，也不會產生模型費用。
- 可以先驗證輸入、教師查詢、輸出格式與 Grounding。
- 可以明確定位錯誤發生在哪一層。
- 可防止模型捏造教師姓名或 Email。
- 後續加入 LLM 後，可比較品質、成本、延遲與失敗率。

### 5.4 能力限制

- 只能查詢固定資料中存在的教師。
- 無法處理姓名錯字、暱稱、英文姓名或模糊稱呼。
- 固定範本的語句較制式。
- 無法深入理解同時包含多個目的的複雜需求。
- `other` 只能使用一般詢問範本。
- 不會即時更新資工系網站資料。
- 不會登入信箱或實際寄送 Email。

## 6. Known Failure

### 6.1 無法辨識非完整教師姓名

固定資料中的姓名為「王小明」，但使用者只輸入「王老師」。Baseline 使用完整姓名進行完全相同比對，因此無法找到教師。

```json
{
  "teacher_name": "王老師",
  "purpose": "project_inquiry",
  "student_name": "李安以",
  "request_details": "想詢問老師下學期是否還有專題生名額"
}
```

### 6.2 實際失敗結果／已執行

- 回傳 HTTP `404`。
- `can_fulfill` 為 `false`。
- `error.code` 為 `TEACHER_NOT_FOUND`。
- `teacher` 與 `email_draft` 均為 `null`。
- `send_status` 為 `not_sent`。
- 不自行推測「王老師」對應哪一位教師。

停止層：Teacher lookup。

### 6.3 後續改善方向

後續可加入姓名正規化與候選教師搜尋。若找到多位可能教師，系統應列出候選人的姓名、職稱及研究領域，要求使用者選擇，不可自行決定收件人。

## 7. 證據狀態

| 項目 | 證據狀態 | 說明 |
| --- | --- | --- |
| 固定教師資料 fixture | 已建立 | 合成教師資料位於 `src/email_draft_baseline.py` |
| Request validation | 已執行／通過 | 已驗證必填欄位與 `purpose` |
| 教師資料查詢 | 已執行／通過 | 已驗證完整姓名比對 |
| Email 草稿產生 | 已執行／通過 | 已驗證固定範本、收件人、主旨與正文 |
| Grounding validation | 已執行／通過 | 已拒絕與 fixture 不一致的收件人 |
| AC01 正常案例 | 已執行／通過 | 核心函式回傳狀態 `200` |
| AC02 缺少必要輸入 | 已執行／通過 | 核心函式回傳狀態 `422` |
| AC03 Email 無依據 | 已執行／通過 | 核心函式回傳狀態 `502` |
| Known Failure | 已執行／通過 | 「王老師」無法通過完整姓名比對並回傳 `404` |
| 實際寄送 Email | 不在本週範圍 | 本週只產生草稿 |

### 7.1 實際執行證據

執行指令：

```bash
python3 -m unittest discover -s tests -v
```

執行摘要：

```text
test_ac01_normal_request_returns_grounded_draft ... ok
test_ac02_missing_teacher_name_stops_at_request_validation ... ok
test_ac03_ungrounded_recipient_is_rejected ... ok
test_known_failure_partial_teacher_name_returns_404 ... ok

Ran 4 tests
OK
```

測試程式位於 `tests/test_email_draft_baseline.py`，受測程式位於 `src/email_draft_baseline.py`。測試未使用網路、API Key 或真實教師資料，也沒有寄出 Email。

### 7.2 尚未提供的工程證據

- 實際 HTTP API Request 與 Response
- HTTP Server 執行紀錄
- pytest 測試結果（目前使用 Python `unittest`）
- 延遲與成本紀錄
- 錯誤與 Failure Log

後續建立 HTTP API 後，需再次執行端對端測試，並附上實際 Request、Response、狀態碼、延遲與錯誤紀錄。

## 8. 初稿自我檢核

- [x] 沿用一個明確的 User Story。
- [x] 列出 In Scope 與 Out of Scope。
- [x] 定義 Request 必填欄位及 Response 最小可驗證欄位。
- [x] 設計正常、非法輸入與 Grounding 失敗三個驗收案例。
- [x] 宣告 Baseline 類型與選擇理由。
- [x] 記錄一個可重現的 Known Failure。
- [x] 核心函式測試與尚未完成的 HTTP API 證據已分開標示。
- [x] 寄信屬於外部操作，本週固定為 `not_sent`。
