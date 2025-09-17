# Jira性能测试工具

基于Locust的Jira性能测试工具，专注于Issue相关操作的性能测试，包括创建、评论、查询和更新等功能。

## 功能特性

- ✅ **Issue创建测试** - 模拟用户创建各种类型的Issue
- ✅ **Issue评论测试** - 为Issue添加评论的性能测试
- ✅ **Issue查询测试** - 测试Issue详情获取和搜索性能
- ✅ **Issue更新测试** - 测试Issue字段更新操作
- ✅ **多用户类型** - 支持普通用户、重负载用户和只读用户
- ✅ **智能数据生成** - 使用Faker生成真实的测试数据
- ✅ **灵活配置** - 通过环境变量管理所有配置

## 项目结构

```
JiraPerformanceTest/
├── config.py              # 配置管理
├── jira_utils.py          # Jira API工具类
├── locustfile.py          # Locust测试主文件
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量模板
└── README.md             # 项目说明
```

## 快速开始

### 1. 环境准备

确保您的系统已安装Python 3.7+：

```powershell
python --version
```

### 2. 安装依赖

```powershell
# 克隆或下载项目到本地
cd c:\Proj\JiraPerformanceTest

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 配置环境

复制环境变量模板并配置您的Jira信息：

```powershell
copy .env.example .env
```

编辑 `.env` 文件，填入您的Jira配置信息：

```env
# Jira服务器地址
JIRA_BASE_URL=https://your-company.atlassian.net

# Jira认证信息（推荐使用API Token）
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-api-token-here

# 测试项目配置
PROJECT_KEY=YOURPROJECT
DEFAULT_ISSUE_TYPE=Task
```

### 4. 获取Jira API Token

1. 登录到 [Atlassian Account](https://id.atlassian.com/manage-profile/security/api-tokens)
2. 点击 "Create API token"
3. 输入标签名称（如 "Performance Test"）
4. 复制生成的Token到 `.env` 文件的 `JIRA_API_TOKEN` 字段

### 5. 运行测试

#### 基本测试（Web界面）
```powershell
locust -f locustfile.py
```
然后在浏览器打开 http://localhost:8089

#### 命令行测试
```powershell
# 模拟10个用户，每秒启动2个用户，运行60秒
locust -f locustfile.py --users 10 --spawn-rate 2 --run-time 60s --headless

# 只使用普通用户类型
locust -f locustfile.py --users 5 --spawn-rate 1 --run-time 30s --headless JiraUser

# 只使用只读用户类型
locust -f locustfile.py --users 10 --spawn-rate 2 --run-time 60s --headless JiraReadOnlyUser
```

## 用户类型说明

### JiraUser（默认用户）
- **创建Issue**: 权重5 - 频繁创建各种Issue
- **添加评论**: 权重3 - 为现有Issue添加评论
- **获取Issue详情**: 权重2 - 查看Issue详细信息
- **搜索Issues**: 权重1 - 执行JQL搜索
- **更新Issue**: 权重1 - 更新Issue描述

### JiraHeavyUser（重负载用户）
- 继承JiraUser的所有功能
- 等待时间更短（0.5-2秒）
- 支持批量创建Issues（2-5个一批）

### JiraReadOnlyUser（只读用户）
- 只进行查询操作，不修改数据
- **获取Issue详情**: 权重8
- **搜索Issues**: 权重5
- 禁用所有写操作

## 配置选项

所有配置通过 `.env` 文件管理：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| JIRA_BASE_URL | Jira服务器地址 | 必填 |
| JIRA_USERNAME | Jira用户名/邮箱 | 必填 |
| JIRA_API_TOKEN | Jira API Token | 推荐 |
| JIRA_PASSWORD | Jira密码 | 不推荐 |
| PROJECT_KEY | 测试项目Key | TEST |
| DEFAULT_ISSUE_TYPE | 默认Issue类型 | Task |
| MAX_WAIT_TIME | 最大等待时间(秒) | 5 |
| MIN_WAIT_TIME | 最小等待时间(秒) | 1 |

## 测试场景详解

### 1. Issue创建测试
- 使用随机生成的标题和描述
- 支持多种Issue类型
- 自动记录创建的Issue Key供后续操作使用

### 2. Issue评论测试
- 优先为已创建的Issue添加评论
- 如无可用Issue，会先搜索现有Issue
- 生成真实的中文评论内容

### 3. Issue查询测试
- 支持多种JQL查询模式
- 包括按创建时间、状态、关键词搜索
- 自动更新可用Issue列表

### 4. Issue更新测试
- 更新Issue描述字段
- 在原描述基础上添加"[更新]"标识

## 性能监控指标

Locust会自动收集以下性能指标：

- **响应时间** - 每个操作的响应时间分布
- **请求频率** - 每秒请求数(RPS)
- **失败率** - 请求失败百分比
- **并发用户数** - 同时在线的虚拟用户数

## 常用测试场景

### 场景1: 基础性能测试
```powershell
# 10用户，运行5分钟
locust -f locustfile.py --users 10 --spawn-rate 2 --run-time 5m --headless
```

### 场景2: 压力测试
```powershell
# 50用户，运行10分钟，使用重负载用户
locust -f locustfile.py --users 50 --spawn-rate 5 --run-time 10m --headless JiraHeavyUser
```

### 场景3: 只读性能测试
```powershell
# 100只读用户，运行15分钟
locust -f locustfile.py --users 100 --spawn-rate 10 --run-time 15m --headless JiraReadOnlyUser
```

### 场景4: 混合负载测试
```powershell
# 启动多个进程模拟不同类型用户
# 终端1: 20个普通用户
locust -f locustfile.py --users 20 --spawn-rate 2 --run-time 10m --headless JiraUser

# 终端2: 30个只读用户
locust -f locustfile.py --users 30 --spawn-rate 3 --run-time 10m --headless JiraReadOnlyUser
```

## 故障排除

### 1. 认证失败
- 检查 `.env` 文件中的用户名和API Token是否正确
- 确认API Token未过期
- 验证用户是否有目标项目的访问权限

### 2. 项目不存在
- 确认 `PROJECT_KEY` 是否正确
- 检查用户是否有该项目的访问权限

### 3. Issue类型错误
- 验证 `DEFAULT_ISSUE_TYPE` 在目标项目中是否存在
- 检查Issue类型名称是否正确（区分大小写）

### 4. 网络连接问题
- 检查 `JIRA_BASE_URL` 是否可访问
- 确认防火墙设置
- 验证SSL证书是否有效

## 扩展功能

### 添加新的测试场景

在 `locustfile.py` 中添加新的 `@task` 方法：

```python
@task(2)
def your_new_test(self):
    """自定义测试场景"""
    # 实现测试逻辑
    pass
```

### 自定义用户行为

创建新的用户类：

```python
class CustomJiraUser(JiraUser):
    """自定义用户行为"""
    wait_time = between(1, 3)
    
    @task(5)
    def custom_behavior(self):
        # 实现自定义行为
        pass
```

### 添加新的API接口

在 `jira_utils.py` 的 `JiraAPIClient` 类中添加新方法：

```python
def your_new_api_call(self, params):
    """新的API调用"""
    url = f"{self.config.api_url}/your-endpoint"
    response = self.session.post(url, json=params)
    return response
```

## 许可证

本项目仅用于性能测试目的，请确保在使用前获得相关授权。

## 支持

如有问题或建议，请创建Issue或提交Pull Request。