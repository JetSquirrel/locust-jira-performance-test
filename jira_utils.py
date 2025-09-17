"""
Jira REST API 工具类
提供issue创建、获取、评论等功能
"""
import json
import requests
from faker import Faker
from config import jira_config

fake = Faker('zh_CN')

class JiraAPIClient:
    """Jira API客户端"""
    
    def __init__(self):
        self.config = jira_config
        self.session = requests.Session()
        self.session.auth = self.config.get_auth()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def create_issue(self, summary=None, description=None, issue_type=None, project_key=None):
        """
        创建issue
        
        Args:
            summary: issue标题
            description: issue描述
            issue_type: issue类型
            project_key: 项目key
            
        Returns:
            tuple: (response对象, issue_key或None)
        """
        if not summary:
            summary = fake.sentence(nb_words=6)
        
        if not description:
            description = fake.text(max_nb_chars=200)
        
        if not issue_type:
            issue_type = self.config.default_issue_type
            
        if not project_key:
            project_key = self.config.project_key
        
        payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": issue_type
                }
            }
        }
        
        url = f"{self.config.api_url}/issue"
        
        try:
            response = self.session.post(url, data=json.dumps(payload))
            
            if response.status_code == 201:
                issue_data = response.json()
                return response, issue_data.get('key')
            else:
                print(f"创建issue失败: {response.status_code} - {response.text}")
                return response, None
                
        except Exception as e:
            print(f"创建issue异常: {str(e)}")
            raise
    
    def get_issue(self, issue_key):
        """
        获取issue详情
        
        Args:
            issue_key: issue的key
            
        Returns:
            requests.Response: 响应对象
        """
        url = f"{self.config.api_url}/issue/{issue_key}"
        
        try:
            response = self.session.get(url)
            return response
        except Exception as e:
            print(f"获取issue异常: {str(e)}")
            raise
    
    def add_comment(self, issue_key, comment_body=None):
        """
        为issue添加评论
        
        Args:
            issue_key: issue的key
            comment_body: 评论内容
            
        Returns:
            requests.Response: 响应对象
        """
        if not comment_body:
            comment_body = fake.text(max_nb_chars=100)
        
        payload = {
            "body": comment_body
        }
        
        url = f"{self.config.api_url}/issue/{issue_key}/comment"
        
        try:
            response = self.session.post(url, data=json.dumps(payload))
            return response
        except Exception as e:
            print(f"添加评论异常: {str(e)}")
            raise
    
    def search_issues(self, jql="project = TEST ORDER BY created DESC", max_results=50):
        """
        搜索issues
        
        Args:
            jql: JQL查询语句
            max_results: 最大返回结果数
            
        Returns:
            requests.Response: 响应对象
        """
        payload = {
            "jql": jql,
            "maxResults": max_results,
            "fields": ["key", "summary", "status", "created"]
        }
        
        url = f"{self.config.api_url}/search"
        
        try:
            response = self.session.post(url, data=json.dumps(payload))
            return response
        except Exception as e:
            print(f"搜索issues异常: {str(e)}")
            raise
    
    def get_project_info(self, project_key=None):
        """
        获取项目信息
        
        Args:
            project_key: 项目key
            
        Returns:
            requests.Response: 响应对象
        """
        if not project_key:
            project_key = self.config.project_key
            
        url = f"{self.config.api_url}/project/{project_key}"
        
        try:
            response = self.session.get(url)
            return response
        except Exception as e:
            print(f"获取项目信息异常: {str(e)}")
            raise
    
    def update_issue(self, issue_key, fields_to_update):
        """
        更新issue
        
        Args:
            issue_key: issue的key
            fields_to_update: 要更新的字段字典
            
        Returns:
            requests.Response: 响应对象
        """
        payload = {
            "fields": fields_to_update
        }
        
        url = f"{self.config.api_url}/issue/{issue_key}"
        
        try:
            response = self.session.put(url, data=json.dumps(payload))
            return response
        except Exception as e:
            print(f"更新issue异常: {str(e)}")
            raise

# 生成测试数据的辅助函数
class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_issue_summary():
        """生成随机的issue标题"""
        prefixes = ["修复", "优化", "新增", "调查", "改进", "实现"]
        subjects = ["用户界面", "数据库连接", "API接口", "页面加载", "搜索功能", "登录模块"]
        return f"{fake.random_element(prefixes)} - {fake.random_element(subjects)} - {fake.word()}"
    
    @staticmethod
    def generate_issue_description():
        """生成随机的issue描述"""
        templates = [
            f"在{fake.date_between(start_date='-30d', end_date='today')}发现问题：{fake.sentence()}",
            f"需要实现以下功能：{fake.text(max_nb_chars=100)}",
            f"用户反馈：{fake.sentence()}，需要调查并修复。",
            f"性能问题：{fake.sentence()}，影响用户体验。"
        ]
        return fake.random_element(templates)
    
    @staticmethod
    def generate_comment():
        """生成随机的评论内容"""
        templates = [
            f"已完成初步调查，发现：{fake.sentence()}",
            f"进展更新：{fake.sentence()}",
            f"需要更多信息：{fake.sentence()}",
            f"测试结果：{fake.sentence()}，建议{fake.word()}。"
        ]
        return fake.random_element(templates)