"""
Jira REST API 工具类
提供SOC安全事件创建、获取、处理记录等功能
"""
import json
import requests
from faker import Faker
from config import jira_config

fake = Faker('en_US')

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
    
    def create_issue(self, summary=None, description=None, issue_type=None, project_key=None, priority=None):
        """
        创建安全事件
        
        Args:
            summary: 安全事件标题
            description: 安全事件描述
            issue_type: 安全事件类型
            project_key: 项目key
            priority: 优先级
            
        Returns:
            tuple: (response对象, issue_key或None)
        """
        if not summary:
            summary = SecurityDataGenerator.generate_security_incident_summary()
        
        if not description:
            description = SecurityDataGenerator.generate_security_incident_description()
        
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
        
        # 添加优先级字段（如果提供）
        if priority:
            payload["fields"]["priority"] = {"name": priority}
        
        url = f"{self.config.api_url}/issue"
        
        try:
            response = self.session.post(url, data=json.dumps(payload))
            
            if response.status_code == 201:
                issue_data = response.json()
                return response, issue_data.get('key')
            else:
                print(f"创建安全事件失败: {response.status_code} - {response.text}")
                return response, None
                
        except Exception as e:
            print(f"创建安全事件异常: {str(e)}")
            raise
    
    def get_issue(self, issue_key):
        """
        获取安全事件详情
        
        Args:
            issue_key: 安全事件的key
            
        Returns:
            requests.Response: 响应对象
        """
        url = f"{self.config.api_url}/issue/{issue_key}"
        
        try:
            response = self.session.get(url)
            return response
        except Exception as e:
            print(f"获取安全事件异常: {str(e)}")
            raise
    
    def add_comment(self, issue_key, comment_body=None):
        """
        为安全事件添加处理记录
        
        Args:
            issue_key: 安全事件的key
            comment_body: 处理记录内容
            
        Returns:
            requests.Response: 响应对象
        """
        if not comment_body:
            comment_body = SecurityDataGenerator.generate_security_comment()
        
        payload = {
            "body": comment_body
        }
        
        url = f"{self.config.api_url}/issue/{issue_key}/comment"
        
        try:
            response = self.session.post(url, data=json.dumps(payload))
            return response
        except Exception as e:
            print(f"添加处理记录异常: {str(e)}")
            raise
    
    def search_issues(self, jql="project = SOC ORDER BY created DESC", max_results=50):
        """
        搜索安全事件
        
        Args:
            jql: JQL查询语句
            max_results: 最大返回结果数
            
        Returns:
            requests.Response: 响应对象
        """
        payload = {
            "jql": jql,
            "maxResults": max_results,
            "fields": ["key", "summary", "status", "created", "priority"]
        }
        
        url = f"{self.config.api_url}/search"
        
        try:
            response = self.session.post(url, data=json.dumps(payload))
            return response
        except Exception as e:
            print(f"搜索安全事件异常: {str(e)}")
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
        更新安全事件
        
        Args:
            issue_key: 安全事件的key
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
            print(f"更新安全事件异常: {str(e)}")
            raise
    
    def assign_incident(self, issue_key, assignee):
        """
        分配安全事件给分析师
        
        Args:
            issue_key: 安全事件的key
            assignee: 分析师用户名
            
        Returns:
            requests.Response: 响应对象
        """
        payload = {
            "fields": {
                "assignee": {
                    "name": assignee
                }
            }
        }
        
        url = f"{self.config.api_url}/issue/{issue_key}"
        
        try:
            response = self.session.put(url, data=json.dumps(payload))
            return response
        except Exception as e:
            print(f"分配安全事件异常: {str(e)}")
            raise
    
    def update_incident_priority(self, issue_key, priority):
        """
        更新安全事件优先级
        
        Args:
            issue_key: 安全事件的key
            priority: 优先级 (Critical, High, Medium, Low)
            
        Returns:
            requests.Response: 响应对象
        """
        payload = {
            "fields": {
                "priority": {
                    "name": priority
                }
            }
        }
        
        url = f"{self.config.api_url}/issue/{issue_key}"
        
        try:
            response = self.session.put(url, data=json.dumps(payload))
            return response
        except Exception as e:
            print(f"更新事件优先级异常: {str(e)}")
            raise
    
    def transition_incident_status(self, issue_key, transition_id, comment=None):
        """
        转换安全事件状态（如：New -> Investigating -> Resolved）
        
        Args:
            issue_key: 安全事件的key
            transition_id: 状态转换ID
            comment: 状态转换说明
            
        Returns:
            requests.Response: 响应对象
        """
        payload = {
            "transition": {
                "id": transition_id
            }
        }
        
        if comment:
            payload["update"] = {
                "comment": [
                    {
                        "add": {
                            "body": comment
                        }
                    }
                ]
            }
        
        url = f"{self.config.api_url}/issue/{issue_key}/transitions"
        
        try:
            response = self.session.post(url, data=json.dumps(payload))
            return response
        except Exception as e:
            print(f"状态转换异常: {str(e)}")
            raise
    
    def create_incident_from_wazuh(self, wazuh_data):
        """
        根据Wazuh告警数据创建安全事件
        
        Args:
            wazuh_data: Wazuh告警数据字典
            
        Returns:
            tuple: (response对象, issue_key或None)
        """
        # 根据Wazuh数据构造事件标题和描述
        rule_id = wazuh_data.get('rule_id', 'Unknown')
        level = wazuh_data.get('level', 0)
        description = wazuh_data.get('description', 'No description')
        agent = wazuh_data.get('agent', {})
        
        summary = f"Wazuh Alert {rule_id}: {description}"
        
        incident_description = f"""
Wazuh Security Alert

Rule ID: {rule_id}
Alert Level: {level}
Description: {description}
Agent: {agent.get('name', 'Unknown')} ({agent.get('ip', 'Unknown')})
Timestamp: {wazuh_data.get('timestamp', 'Unknown')}

Raw Alert Data:
{json.dumps(wazuh_data, indent=2)}
        """
        
        # 根据告警级别设置优先级
        priority_map = {
            15: "Critical",
            12: "High", 
            10: "High",
            7: "Medium",
            5: "Medium", 
            3: "Low",
            1: "Low"
        }
        
        priority = priority_map.get(level, "Medium")
        
        return self.create_issue(
            summary=summary.strip(),
            description=incident_description.strip(),
            issue_type="Security Incident",
            priority=priority
        )

# 生成SOC安全事件测试数据的辅助函数
class SecurityDataGenerator:
    """SOC安全事件数据生成器"""
    
    # 威胁类型和攻击向量
    THREAT_TYPES = [
        "Malware Detection", "Network Intrusion", "Suspicious Login", 
        "Data Exfiltration", "Phishing Attempt", "Vulnerability Exploit",
        "Brute Force Attack", "DDoS Attack", "Insider Threat", "APT Activity"
    ]
    
    ATTACK_VECTORS = [
        "Email", "Web Application", "Network", "Endpoint", "Cloud Services",
        "Remote Access", "Mobile Device", "IoT Device", "Database", "API"
    ]
    
    IOC_TYPES = [
        "IP Address", "Domain Name", "File Hash", "URL", "Email Address",
        "Registry Key", "Process Name", "User Account", "Certificate"
    ]
    
    SEVERITY_LEVELS = ["Critical", "High", "Medium", "Low", "Info"]
    
    @staticmethod
    def generate_security_incident_summary():
        """生成安全事件标题"""
        threat_type = fake.random_element(SecurityDataGenerator.THREAT_TYPES)
        attack_vector = fake.random_element(SecurityDataGenerator.ATTACK_VECTORS)
        
        templates = [
            f"{threat_type} detected via {attack_vector}",
            f"Suspicious {threat_type} activity on {attack_vector}",
            f"Alert: {threat_type} targeting {attack_vector}",
            f"Security Event: {threat_type} through {attack_vector}",
            f"Incident: Potential {threat_type} using {attack_vector}"
        ]
        
        return fake.random_element(templates)
    
    @staticmethod
    def generate_security_incident_description():
        """生成安全事件描述"""
        source_ip = fake.ipv4()
        dest_ip = fake.ipv4()
        timestamp = fake.date_time_between(start_date='-7d', end_date='now')
        user_agent = fake.user_agent()
        
        templates = [
            f"Wazuh Alert Details:\n"
            f"- Timestamp: {timestamp}\n"
            f"- Source IP: {source_ip}\n"
            f"- Destination IP: {dest_ip}\n"
            f"- User Agent: {user_agent}\n"
            f"- Rule ID: {fake.random_int(min=1000, max=9999)}\n"
            f"- Alert Level: {fake.random_int(min=1, max=15)}\n"
            f"- Description: {fake.sentence()}",
            
            f"SIEM Alert Triggered:\n"
            f"- Event Time: {timestamp}\n"
            f"- Affected Asset: {fake.hostname()}\n"
            f"- Source: {source_ip}\n"
            f"- IOC: {SecurityDataGenerator.generate_ioc()}\n"
            f"- Risk Score: {fake.random_int(min=1, max=100)}\n"
            f"- Additional Context: {fake.text(max_nb_chars=100)}",
            
            f"Security Event Detected:\n"
            f"- Detection Time: {timestamp}\n"
            f"- Endpoint: {fake.hostname()}\n"
            f"- Process: {fake.file_name()}\n"
            f"- Command Line: {fake.text(max_nb_chars=80)}\n"
            f"- Hash: {fake.sha256()}\n"
            f"- Analyst Notes: Initial triage required"
        ]
        
        return fake.random_element(templates)
    
    @staticmethod
    def generate_security_comment():
        """生成安全处理记录"""
        analyst_name = fake.first_name()
        
        templates = [
            f"[{analyst_name}] Initial triage completed. {fake.sentence()} Escalating to L2 for further analysis.",
            f"[{analyst_name}] Investigation in progress. {fake.sentence()} Checking threat intelligence feeds.",
            f"[{analyst_name}] False positive confirmed. {fake.sentence()} Updating detection rules to reduce noise.",
            f"[{analyst_name}] Containment actions taken. {fake.sentence()} Monitoring for additional indicators.",
            f"[{analyst_name}] Incident resolved. {fake.sentence()} Root cause analysis completed.",
            f"[{analyst_name}] IOC analysis: {SecurityDataGenerator.generate_ioc()} - {fake.sentence()}",
            f"[{analyst_name}] Timeline analysis: {fake.sentence()} Event correlation with other incidents ongoing.",
            f"[{analyst_name}] User behavior analysis: {fake.sentence()} No anomalies detected in recent activity.",
            f"[{analyst_name}] Network forensics: {fake.sentence()} Packet capture analysis in progress.",
            f"[{analyst_name}] Malware analysis: {fake.sentence()} Sandbox execution results attached."
        ]
        
        return fake.random_element(templates)
    
    @staticmethod
    def generate_ioc():
        """生成威胁指标"""
        ioc_type = fake.random_element(SecurityDataGenerator.IOC_TYPES)
        
        ioc_generators = {
            "IP Address": lambda: fake.ipv4(),
            "Domain Name": lambda: fake.domain_name(),
            "File Hash": lambda: fake.sha256(),
            "URL": lambda: fake.url(),
            "Email Address": lambda: fake.email(),
            "Registry Key": lambda: f"HKEY_LOCAL_MACHINE\\{fake.word()}\\{fake.word()}",
            "Process Name": lambda: f"{fake.word()}.exe",
            "User Account": lambda: fake.user_name(),
            "Certificate": lambda: f"CN={fake.company()}, O={fake.company()}"
        }
        
        ioc_value = ioc_generators.get(ioc_type, lambda: fake.word())()
        return f"{ioc_type}: {ioc_value}"
    
    @staticmethod
    def generate_wazuh_alert_data():
        """生成Wazuh告警数据格式"""
        return {
            "rule_id": fake.random_int(min=1000, max=99999),
            "level": fake.random_int(min=1, max=15),
            "description": fake.sentence(),
            "groups": [fake.word(), fake.word()],
            "timestamp": fake.date_time_between(start_date='-1d', end_date='now').isoformat(),
            "agent": {
                "id": f"{fake.random_int(min=1, max=1000):03d}",
                "name": fake.hostname(),
                "ip": fake.ipv4()
            },
            "data": {
                "srcip": fake.ipv4(),
                "dstip": fake.ipv4(),
                "srcport": fake.random_int(min=1024, max=65535),
                "dstport": fake.random_int(min=1, max=1023),
                "protocol": fake.random_element(["TCP", "UDP", "ICMP"]),
                "action": fake.random_element(["ALLOW", "DENY", "DROP"])
            }
        }
    
    @staticmethod
    def generate_soc_jql_queries():
        """生成SOC常用的JQL查询语句"""
        project_key = "SOC"  # 假设SOC项目key
        
        queries = [
            f'project = {project_key} AND priority = "Critical" AND status != "Resolved" ORDER BY created DESC',
            f'project = {project_key} AND summary ~ "Malware" AND created >= -24h ORDER BY priority DESC',
            f'project = {project_key} AND assignee = currentUser() AND status = "In Progress" ORDER BY updated DESC',
            f'project = {project_key} AND labels in ("APT", "targeted-attack") ORDER BY created DESC',
            f'project = {project_key} AND status = "New" AND created >= -8h ORDER BY priority DESC, created DESC',
            f'project = {project_key} AND description ~ "phishing" AND created >= -7d ORDER BY created DESC',
            f'project = {project_key} AND priority in ("Critical", "High") AND assignee is EMPTY ORDER BY created ASC',
            f'project = {project_key} AND summary ~ "brute.force" AND resolved >= -30d ORDER BY resolved DESC'
        ]
        
        return fake.random_element(queries)

# SOC测试场景辅助类
class SOCTestScenarios:
    """SOC测试场景生成器"""
    
    def __init__(self, jira_client):
        self.jira_client = jira_client
    
    def simulate_wazuh_batch_alerts(self, batch_size=10):
        """
        模拟Wazuh批量告警导入
        
        Args:
            batch_size: 批量大小
            
        Returns:
            list: 创建的安全事件列表
        """
        created_incidents = []
        
        for i in range(batch_size):
            wazuh_data = SecurityDataGenerator.generate_wazuh_alert_data()
            response, issue_key = self.jira_client.create_incident_from_wazuh(wazuh_data)
            
            if issue_key:
                created_incidents.append({
                    'issue_key': issue_key,
                    'wazuh_data': wazuh_data,
                    'response': response
                })
        
        return created_incidents
    
    def simulate_shift_handover(self, outgoing_analyst, incoming_analyst, incident_keys):
        """
        模拟值班交接场景
        
        Args:
            outgoing_analyst: 交班分析师
            incoming_analyst: 接班分析师
            incident_keys: 需要交接的事件列表
            
        Returns:
            list: 交接结果
        """
        handover_results = []
        
        for incident_key in incident_keys:
            # 添加交接记录
            handover_comment = f"Shift handover from {outgoing_analyst} to {incoming_analyst}. " \
                             f"Current status and investigation notes transferred. " \
                             f"{fake.sentence()}"
            
            comment_response = self.jira_client.add_comment(incident_key, handover_comment)
            
            # 重新分配给接班分析师
            assign_response = self.jira_client.assign_incident(incident_key, incoming_analyst)
            
            handover_results.append({
                'incident_key': incident_key,
                'comment_response': comment_response,
                'assign_response': assign_response
            })
        
        return handover_results
    
    def simulate_incident_escalation(self, incident_key, from_priority, to_priority, reason=None):
        """
        模拟事件升级场景
        
        Args:
            incident_key: 事件key
            from_priority: 原优先级
            to_priority: 新优先级
            reason: 升级原因
            
        Returns:
            dict: 升级结果
        """
        if not reason:
            reason = f"Escalation required due to {fake.sentence()}"
        
        # 更新优先级
        priority_response = self.jira_client.update_incident_priority(incident_key, to_priority)
        
        # 添加升级说明
        escalation_comment = f"Priority escalated from {from_priority} to {to_priority}. " \
                           f"Reason: {reason} " \
                           f"Escalation time: {fake.date_time_between(start_date='-1h', end_date='now')}"
        
        comment_response = self.jira_client.add_comment(incident_key, escalation_comment)
        
        return {
            'incident_key': incident_key,
            'priority_response': priority_response,
            'comment_response': comment_response,
            'escalation_reason': reason
        }
    
    def generate_realistic_soc_workload(self, num_incidents=50):
        """
        生成真实的SOC工作负载数据
        
        Args:
            num_incidents: 要生成的事件数量
            
        Returns:
            dict: 生成的工作负载统计
        """
        incident_distribution = {
            'Critical': int(num_incidents * 0.05),  # 5%
            'High': int(num_incidents * 0.15),      # 15%
            'Medium': int(num_incidents * 0.35),    # 35%
            'Low': int(num_incidents * 0.35),       # 35%
            'Info': int(num_incidents * 0.10)       # 10%
        }
        
        created_incidents = {
            'Critical': [],
            'High': [],
            'Medium': [],
            'Low': [],
            'Info': []
        }
        
        for priority, count in incident_distribution.items():
            for i in range(count):
                summary = SecurityDataGenerator.generate_security_incident_summary()
                description = SecurityDataGenerator.generate_security_incident_description()
                
                response, issue_key = self.jira_client.create_issue(
                    summary=summary,
                    description=description,
                    issue_type="Security Incident",
                    priority=priority
                )
                
                if issue_key:
                    created_incidents[priority].append(issue_key)
        
        return {
            'total_created': sum(len(incidents) for incidents in created_incidents.values()),
            'distribution': {k: len(v) for k, v in created_incidents.items()},
            'incidents': created_incidents
        }