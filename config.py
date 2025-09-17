"""
Jira性能测试配置管理
"""
import os
from decouple import config

class JiraConfig:
    """Jira配置类"""
    
    def __init__(self):
        # Jira服务器配置
        self.base_url = config('JIRA_BASE_URL', default='https://your-domain.atlassian.net')
        self.api_url = f"{self.base_url}/rest/api/2"
        
        # 认证配置
        self.username = config('JIRA_USERNAME', default='')
        self.api_token = config('JIRA_API_TOKEN', default='')
        self.password = config('JIRA_PASSWORD', default='')
        
        # 项目配置
        self.project_key = config('PROJECT_KEY', default='TEST')
        self.default_issue_type = config('DEFAULT_ISSUE_TYPE', default='Task')
        
        # 性能测试配置
        self.max_wait_time = config('MAX_WAIT_TIME', default=5, cast=int)
        self.min_wait_time = config('MIN_WAIT_TIME', default=1, cast=int)
        
    def get_auth(self):
        """获取认证信息"""
        if self.api_token:
            return (self.username, self.api_token)
        elif self.password:
            return (self.username, self.password)
        else:
            raise ValueError("必须提供API Token或密码进行认证")
    
    def validate_config(self):
        """验证配置是否完整"""
        if not self.base_url or self.base_url == 'https://your-domain.atlassian.net':
            raise ValueError("请在.env文件中设置正确的JIRA_BASE_URL")
        
        if not self.username:
            raise ValueError("请在.env文件中设置JIRA_USERNAME")
        
        if not self.api_token and not self.password:
            raise ValueError("请在.env文件中设置JIRA_API_TOKEN或JIRA_PASSWORD")
        
        if not self.project_key or self.project_key == 'TEST':
            print("警告: 使用默认项目KEY 'TEST'，建议设置PROJECT_KEY")
        
        return True

# 全局配置实例
jira_config = JiraConfig()