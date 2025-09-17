"""
Jira性能测试 - Locust测试脚本
主要测试issue的创建和评论功能
"""
import random
from locust import HttpUser, task, between
from jira_utils import JiraAPIClient, TestDataGenerator
from config import jira_config

class JiraUser(HttpUser):
    """Jira用户行为模拟"""
    
    # 等待时间设置（秒）
    wait_time = between(jira_config.min_wait_time, jira_config.max_wait_time)
    
    def on_start(self):
        """每个用户开始时执行的初始化操作"""
        try:
            # 验证配置
            jira_config.validate_config()
            
            # 初始化Jira API客户端
            self.jira_client = JiraAPIClient()
            
            # 设置Locust的HTTP客户端基础URL和认证
            self.client.base_url = jira_config.base_url
            self.client.auth = jira_config.get_auth()
            self.client.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
            # 存储创建的issue keys，用于后续操作
            self.created_issues = []
            
            # 验证连接
            self._verify_connection()
            
            print(f"用户初始化完成，目标Jira: {jira_config.base_url}")
            
        except Exception as e:
            print(f"用户初始化失败: {str(e)}")
            raise
    
    def _verify_connection(self):
        """验证Jira连接"""
        try:
            response = self.jira_client.get_project_info()
            if response.status_code != 200:
                raise Exception(f"无法连接到项目 {jira_config.project_key}: {response.status_code}")
            print(f"成功连接到项目: {jira_config.project_key}")
        except Exception as e:
            print(f"连接验证失败: {str(e)}")
            raise
    
    @task(5)
    def create_issue(self):
        """创建issue任务（权重5，执行频率较高）"""
        try:
            summary = TestDataGenerator.generate_issue_summary()
            description = TestDataGenerator.generate_issue_description()
            
            # 使用Locust的HTTP客户端进行请求，以便统计性能指标
            payload = {
                "fields": {
                    "project": {
                        "key": jira_config.project_key
                    },
                    "summary": summary,
                    "description": description,
                    "issuetype": {
                        "name": jira_config.default_issue_type
                    }
                }
            }
            
            with self.client.post(
                "/rest/api/2/issue",
                json=payload,
                name="创建Issue",
                catch_response=True
            ) as response:
                if response.status_code == 201:
                    issue_data = response.json()
                    issue_key = issue_data.get('key')
                    if issue_key:
                        self.created_issues.append(issue_key)
                        response.success()
                        print(f"✓ 成功创建issue: {issue_key}")
                    else:
                        response.failure("创建issue成功但未返回key")
                else:
                    response.failure(f"创建issue失败: {response.status_code}")
                    
        except Exception as e:
            print(f"✗ 创建issue异常: {str(e)}")
    
    @task(3)
    def add_comment_to_existing_issue(self):
        """为已存在的issue添加评论（权重3）"""
        if not self.created_issues:
            # 如果没有创建过issue，先搜索一些现有的
            self._search_existing_issues()
        
        if self.created_issues:
            issue_key = random.choice(self.created_issues)
            comment_body = TestDataGenerator.generate_comment()
            
            try:
                payload = {
                    "body": comment_body
                }
                
                with self.client.post(
                    f"/rest/api/2/issue/{issue_key}/comment",
                    json=payload,
                    name="添加评论",
                    catch_response=True
                ) as response:
                    if response.status_code == 201:
                        response.success()
                        print(f"✓ 成功为 {issue_key} 添加评论")
                    else:
                        response.failure(f"添加评论失败: {response.status_code}")
                        
            except Exception as e:
                print(f"✗ 添加评论异常: {str(e)}")
        else:
            print("没有可用的issue来添加评论")
    
    @task(2)
    def get_issue_details(self):
        """获取issue详情（权重2）"""
        if not self.created_issues:
            self._search_existing_issues()
        
        if self.created_issues:
            issue_key = random.choice(self.created_issues)
            
            try:
                with self.client.get(
                    f"/rest/api/2/issue/{issue_key}",
                    name="获取Issue详情",
                    catch_response=True
                ) as response:
                    if response.status_code == 200:
                        response.success()
                        print(f"✓ 成功获取 {issue_key} 详情")
                    else:
                        response.failure(f"获取issue详情失败: {response.status_code}")
                        
            except Exception as e:
                print(f"✗ 获取issue详情异常: {str(e)}")
    
    @task(1)
    def search_issues(self):
        """搜索issues（权重1，执行频率较低）"""
        try:
            jql_queries = [
                f"project = {jira_config.project_key} ORDER BY created DESC",
                f"project = {jira_config.project_key} AND status = 'To Do' ORDER BY created DESC",
                f"project = {jira_config.project_key} AND created >= -7d ORDER BY created DESC",
                f"project = {jira_config.project_key} AND summary ~ 'test*' ORDER BY created DESC"
            ]
            
            jql = random.choice(jql_queries)
            payload = {
                "jql": jql,
                "maxResults": 20,
                "fields": ["key", "summary", "status", "created"]
            }
            
            with self.client.post(
                "/rest/api/2/search",
                json=payload,
                name="搜索Issues",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    search_data = response.json()
                    issues_found = len(search_data.get('issues', []))
                    response.success()
                    print(f"✓ 搜索完成，找到 {issues_found} 个issues")
                    
                    # 更新可用的issue列表
                    for issue in search_data.get('issues', []):
                        issue_key = issue.get('key')
                        if issue_key and issue_key not in self.created_issues:
                            self.created_issues.append(issue_key)
                    
                else:
                    response.failure(f"搜索issues失败: {response.status_code}")
                    
        except Exception as e:
            print(f"✗ 搜索issues异常: {str(e)}")
    
    @task(1)
    def update_issue_description(self):
        """更新issue描述（权重1）"""
        if not self.created_issues:
            self._search_existing_issues()
        
        if self.created_issues:
            issue_key = random.choice(self.created_issues)
            new_description = f"[更新] {TestDataGenerator.generate_issue_description()}"
            
            try:
                payload = {
                    "fields": {
                        "description": new_description
                    }
                }
                
                with self.client.put(
                    f"/rest/api/2/issue/{issue_key}",
                    json=payload,
                    name="更新Issue",
                    catch_response=True
                ) as response:
                    if response.status_code == 204:
                        response.success()
                        print(f"✓ 成功更新 {issue_key} 描述")
                    else:
                        response.failure(f"更新issue失败: {response.status_code}")
                        
            except Exception as e:
                print(f"✗ 更新issue异常: {str(e)}")
    
    def _search_existing_issues(self):
        """搜索现有issues以填充issue列表"""
        try:
            response = self.jira_client.search_issues(
                jql=f"project = {jira_config.project_key} ORDER BY created DESC",
                max_results=10
            )
            
            if response.status_code == 200:
                search_data = response.json()
                for issue in search_data.get('issues', []):
                    issue_key = issue.get('key')
                    if issue_key and issue_key not in self.created_issues:
                        self.created_issues.append(issue_key)
                        
                print(f"搜索到 {len(self.created_issues)} 个可用issues")
            else:
                print(f"搜索现有issues失败: {response.status_code}")
                
        except Exception as e:
            print(f"搜索现有issues异常: {str(e)}")

class JiraHeavyUser(JiraUser):
    """重负载Jira用户（更频繁的操作）"""
    
    # 更短的等待时间
    wait_time = between(0.5, 2)
    
    @task(10)
    def create_multiple_issues(self):
        """批量创建issues"""
        batch_size = random.randint(2, 5)
        for i in range(batch_size):
            self.create_issue()

class JiraReadOnlyUser(JiraUser):
    """只读用户（只进行查询操作）"""
    
    wait_time = between(1, 3)
    
    @task(8)
    def get_issue_details(self):
        """获取issue详情（重写为更高权重）"""
        super().get_issue_details()
    
    @task(5)
    def search_issues(self):
        """搜索issues（重写为更高权重）"""
        super().search_issues()
    
    @task(0)
    def create_issue(self):
        """禁用创建issue"""
        pass
    
    @task(0)
    def add_comment_to_existing_issue(self):
        """禁用添加评论"""
        pass
    
    @task(0)
    def update_issue_description(self):
        """禁用更新issue"""
        pass