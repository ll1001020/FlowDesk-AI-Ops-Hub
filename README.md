# FlowDesk AI Ops Hub

一个可真实落地的 **多行业知识库 + 工单处置 + AI Agent 工作台**。

它不绑定任何单一模型或厂商，默认使用本地 Mock LLM 演示；上线时可以切换到任意 OpenAI-compatible API、企业私有模型、本地 Ollama 服务或其他大模型网关。

## 适合申请/展示的项目定位

**项目名称：FlowDesk AI Ops Hub**

**一句话介绍：**
面向门店运维、电商客服、校园后勤、设备巡检等场景，把分散的 SOP、FAQ、故障手册和历史工单转化为可追溯的 AI 处置助手，帮助一线人员快速定位问题、生成处理步骤、沉淀工单闭环。

## 核心能力

- 多场景知识库 RAG：支持门店、客服、校园、设备巡检等文档接入
- 工单智能分级：自动识别风险等级、责任团队、建议 SLA
- 处置步骤生成：基于检索到的 SOP 生成可执行 checklist
- 多模型适配：Mock / OpenAI-compatible / Ollama / 自定义 HTTP 网关
- 可审计输出：每次回答都返回引用片段与检索分数
- 工单沉淀：SQLite 存储问题、模型回答、状态和标签
- Web Demo：浏览器可直接体验，不依赖复杂前端构建
- API-first：方便嵌入企业微信、钉钉、飞书、客服后台或巡检系统

## 技术栈

- Backend: FastAPI + SQLite + Pydantic
- RAG: 轻量 TF-IDF / cosine 检索，便于演示和二次开发
- Frontend: 原生 HTML/CSS/JS
- Tests: pytest
- Deployment: Dockerfile

## 快速启动

```bash
cd flowdesk-ai-ops-hub
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

打开浏览器：

```text
http://127.0.0.1:8000
```

## 模型配置

默认无需配置，使用 Mock LLM，方便演示。

复制环境变量模板：

```bash
cp .env.example .env
```

### 使用 OpenAI-compatible API

只要目标模型平台兼容 `/chat/completions`，即可这样配置：

```bash
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://your-model-gateway.example.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL=your-model-name
```

### 使用 Ollama

```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
LLM_MODEL=qwen2.5:7b
```

### 使用 Mock

```bash
LLM_PROVIDER=mock
```

## API 示例

### 1. AI 处置建议

```bash
curl -X POST http://127.0.0.1:8000/api/assist \
  -H 'Content-Type: application/json' \
  -d '{"question":"门店收银机突然无法扫码，顾客排队严重，应该怎么处理？","scenario":"retail_ops"}'
```

### 2. 创建工单

```bash
curl -X POST http://127.0.0.1:8000/api/tickets \
  -H 'Content-Type: application/json' \
  -d '{"title":"收银机无法扫码","description":"门店 A 收银机扫码枪无响应，影响结账","scenario":"retail_ops"}'
```

### 3. 查看工单

```bash
curl http://127.0.0.1:8000/api/tickets
```

## 目录结构

```text
flowdesk-ai-ops-hub/
├── app/
│   ├── main.py                # FastAPI 入口
│   ├── agent.py               # Agent 编排：检索、分级、生成、落库
│   ├── config.py              # 环境变量配置
│   ├── db.py                  # SQLite 存储
│   ├── rag.py                 # 轻量 RAG 检索
│   ├── schemas.py             # API 数据模型
│   ├── providers/             # 多模型适配层
│   └── static/                # 前端页面
├── data/knowledge/            # 多行业知识库样例
├── tests/                     # 单元测试
├── APPLICATION_MATERIAL.md    # 申请材料草稿
├── Dockerfile
└── requirements.txt
```

## 可继续扩展

- 接入企业微信/飞书/钉钉机器人
- 接入真实客服系统或 CMDB
- 上传 PDF/Word 自动切分入库
- 增加向量数据库：FAISS / Milvus / pgvector
- 增加多租户权限与角色控制
- 增加模型效果评测集与 A/B 测试

## 演示问题

你可以在页面输入：

- 门店收银机无法扫码，顾客排队严重，怎么处理？
- 用户反馈包裹已显示签收但没收到，客服怎么回复？
- 教学楼空调漏水，现场人员应该先做什么？
- 巡检发现设备温度过高但还没停机，风险怎么判断？
