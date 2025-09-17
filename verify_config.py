"""
Jira配置验证脚本
在运行性能测试前使用此脚本验证配置是否正确
"""
import sys
from config import jira_config
from jira_utils import JiraAPIClient

def main():
    """主函数"""
    print("=== Jira性能测试配置验证 ===\n")
    
    try:
        # 1. 验证配置
        print("1. 验证配置文件...")
        jira_config.validate_config()
        print("✓ 配置文件验证通过")
        
        # 2. 显示配置信息
        print(f"\n2. 配置信息:")
        print(f"   Jira服务器: {jira_config.base_url}")
        print(f"   用户名: {jira_config.username}")
        print(f"   项目Key: {jira_config.project_key}")
        print(f"   Issue类型: {jira_config.default_issue_type}")
        print(f"   认证方式: {'API Token' if jira_config.api_token else 'Password'}")
        
        # 3. 测试连接
        print(f"\n3. 测试Jira连接...")
        client = JiraAPIClient()
        
        # 测试项目访问
        project_response = client.get_project_info()
        if project_response.status_code == 200:
            project_data = project_response.json()
            print(f"✓ 成功连接到项目: {project_data.get('name', 'Unknown')}")
            print(f"   项目Key: {project_data.get('key')}")
            print(f"   项目类型: {project_data.get('projectTypeKey')}")
        else:
            print(f"✗ 项目连接失败: {project_response.status_code}")
            print(f"   错误信息: {project_response.text}")
            return False
        
        # 4. 测试搜索功能
        print(f"\n4. 测试Issue搜索...")
        search_response = client.search_issues(max_results=5)
        if search_response.status_code == 200:
            search_data = search_response.json()
            total_issues = search_data.get('total', 0)
            print(f"✓ 搜索功能正常，项目中共有 {total_issues} 个Issues")
            
            # 显示最近的几个issues
            issues = search_data.get('issues', [])
            if issues:
                print("   最近的Issues:")
                for issue in issues[:3]:
                    print(f"   - {issue.get('key')}: {issue.get('fields', {}).get('summary', 'No summary')}")
        else:
            print(f"✗ 搜索功能测试失败: {search_response.status_code}")
            print(f"   错误信息: {search_response.text}")
        
        # 5. 测试创建Issue（可选）
        print(f"\n5. 测试Issue创建权限...")
        test_response, test_issue_key = client.create_issue(
            summary="[测试] 配置验证测试Issue - 请忽略",
            description="这是一个配置验证测试Issue，可以安全删除。"
        )
        
        if test_response.status_code == 201 and test_issue_key:
            print(f"✓ Issue创建权限正常，测试Issue: {test_issue_key}")
            print(f"   注意: 请手动删除测试Issue {test_issue_key}")
        else:
            print(f"⚠ Issue创建测试失败: {test_response.status_code}")
            print(f"   这可能是权限问题，但不影响只读测试")
            print(f"   错误信息: {test_response.text}")
        
        print(f"\n=== 配置验证完成 ===")
        print(f"✓ 基本配置正确，可以开始性能测试")
        print(f"\n使用以下命令启动测试:")
        print(f"   基础测试: locust -f locustfile.py")
        print(f"   命令行测试: locust -f locustfile.py --users 5 --spawn-rate 1 --run-time 30s --headless")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 配置验证失败: {str(e)}")
        print(f"\n请检查以下事项:")
        print(f"1. .env文件是否存在且配置正确")
        print(f"2. Jira服务器地址是否可访问")
        print(f"3. 用户名和API Token是否有效")
        print(f"4. 项目Key是否正确")
        print(f"5. 用户是否有项目访问权限")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)