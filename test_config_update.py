#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZBProxy配置更新测试脚本
用于测试ZBProxy管理API的配置更新功能
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# API配置
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def print_separator(title: str = ""):
    """打印分隔线"""
    print("\n" + "="*60)
    if title:
        print(f" {title} ")
        print("="*60)

def print_result(operation: str, response: requests.Response, expected_success: bool = True):
    """打印操作结果"""
    print(f"\n🔧 {operation}")
    print(f"状态码: {response.status_code}")
    
    try:
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if expected_success:
            if response.status_code == 200 and result.get("success", False):
                print("✅ 操作成功")
            else:
                print("❌ 操作失败")
        else:
            print("ℹ️  预期操作（可能失败）")
    except json.JSONDecodeError:
        print(f"响应内容: {response.text}")
        print("❌ 无法解析JSON响应")

def get_config() -> Dict[str, Any]:
    """获取当前配置"""
    try:
        response = requests.get(f"{BASE_URL}/config")
        if response.status_code == 200:
            return response.json().get("config", {})
        else:
            print(f"❌ 获取配置失败: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ 获取配置异常: {e}")
        return {}

def get_config_value(path: str):
    """获取指定路径的配置值"""
    try:
        response = requests.get(f"{BASE_URL}/config/{path}")
        print_result(f"获取配置值: {path}", response)
        return response
    except Exception as e:
        print(f"❌ 获取配置值异常: {e}")
        return None

def update_config(path: str, value: Any, description: str = ""):
    """更新配置值"""
    data = {"path": path, "value": value}
    try:
        response = requests.put(f"{BASE_URL}/config", json=data, headers=HEADERS)
        operation_desc = f"更新配置 {path} = {value}"
        if description:
            operation_desc += f" ({description})"
        print_result(operation_desc, response)
        return response
    except Exception as e:
        print(f"❌ 更新配置异常: {e}")
        return None

def test_basic_config_updates():
    """测试基本配置更新"""
    print_separator("基本配置更新测试")
    
    # 测试用例列表
    test_cases = [
        # (路径, 新值, 描述)
        ("Log.Level", "debug", "修改日志级别为debug"),
        ("Log.Level", "info", "修改日志级别为info"),
        ("Log.Level", "error", "修改日志级别为error"),
        ("Router.DefaultOutbound", "TestOutbound", "修改默认出站"),
    ]
    
    for path, value, description in test_cases:
        # 先获取原始值
        print(f"\n📋 测试: {description}")
        get_config_value(path)
        
        # 更新配置
        update_config(path, value, description)
        
        # 验证更新结果
        time.sleep(0.5)  # 短暂等待
        get_config_value(path)

def test_service_config_updates():
    """测试服务配置更新"""
    print_separator("服务配置更新测试")
    
    # 先获取当前服务配置
    config = get_config()
    services = config.get("Services", [])
    
    if not services:
        print("⚠️  没有找到服务配置，跳过服务配置测试")
        return
    
    print(f"📋 当前有 {len(services)} 个服务配置")
    
    # 测试修改第一个服务的配置
    if len(services) > 0:
        test_cases = [
            ("Services.0.Listen", 25566, "修改第一个服务监听端口"),
            ("Services.0.Listen", 25565, "恢复第一个服务监听端口"),
            ("Services.0.IPAccess.Mode", "whitelist", "设置IP访问模式为白名单"),
            ("Services.0.IPAccess.Mode", "", "清空IP访问模式"),
        ]
        
        for path, value, description in test_cases:
            print(f"\n📋 测试: {description}")
            get_config_value(path)
            update_config(path, value, description)
            time.sleep(0.5)
            get_config_value(path)

def test_outbound_config_updates():
    """测试出站配置更新"""
    print_separator("出站配置更新测试")
    
    # 先获取当前出站配置
    config = get_config()
    outbounds = config.get("Outbounds", [])
    
    if not outbounds:
        print("⚠️  没有找到出站配置，跳过出站配置测试")
        return
    
    print(f"📋 当前有 {len(outbounds)} 个出站配置")
    
    # 测试修改第一个出站的配置
    if len(outbounds) > 0:
        test_cases = [
            ("Outbounds.0.TargetAddress", "mc.example.com", "修改目标地址"),
            ("Outbounds.0.TargetPort", 25566, "修改目标端口"),
            ("Outbounds.0.Minecraft.OnlineCount.Max", 100, "修改最大在线人数"),
            ("Outbounds.0.Minecraft.EnableHostnameRewrite", False, "禁用主机名重写"),
            # 恢复原始设置
            ("Outbounds.0.TargetAddress", "mc.hypixel.net", "恢复目标地址"),
            ("Outbounds.0.TargetPort", 25565, "恢复目标端口"),
            ("Outbounds.0.Minecraft.OnlineCount.Max", 20, "恢复最大在线人数"),
            ("Outbounds.0.Minecraft.EnableHostnameRewrite", True, "启用主机名重写"),
        ]
        
        for path, value, description in test_cases:
            print(f"\n📋 测试: {description}")
            get_config_value(path)
            update_config(path, value, description)
            time.sleep(0.5)
            get_config_value(path)

def test_complex_config_updates():
    """测试复杂配置更新"""
    print_separator("复杂配置更新测试")
    
    # 测试复杂对象更新
    complex_test_cases = [
        (
            "Outbounds.0.Minecraft.OnlineCount",
            {"Max": 50, "Online": -1, "EnableMaxLimit": True},
            "更新在线人数配置对象"
        ),
        (
            "Router.Rules.0.Rewrite",
            {"hostname": "custom.server.com", "port": 25565},
            "更新路由重写规则"
        ),
        (
            "Outbounds.0.Minecraft.MotdDescription",
            "§a欢迎来到测试服务器§r\n§e正在进行配置测试",
            "更新MOTD描述"
        ),
    ]
    
    for path, value, description in complex_test_cases:
        print(f"\n📋 测试: {description}")
        get_config_value(path)
        update_config(path, value, description)
        time.sleep(0.5)
        get_config_value(path)

def test_invalid_config_updates():
    """测试无效配置更新"""
    print_separator("无效配置更新测试")
    
    # 测试无效路径和值
    invalid_test_cases = [
        ("NonExistent.Path", "value", "测试不存在的路径"),
        ("Services.999.Listen", 25565, "测试无效的数组索引"),
        ("Log", {"invalid": "object"}, "测试无效的值类型"),
        ("Services.0.Listen", "invalid_port", "测试无效的端口值"),
        ("Services.0.Listen", -1, "测试负数端口"),
        ("Services.0.Listen", 99999, "测试过大的端口号"),
    ]
    
    for path, value, description in invalid_test_cases:
        print(f"\n📋 测试: {description}")
        update_config(path, value, description)

def test_api_connectivity():
    """测试API连接性"""
    print_separator("API连接性测试")
    
    try:
        # 测试根路径
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print_result("连接根路径", response)
        
        # 测试获取配置
        response = requests.get(f"{BASE_URL}/config", timeout=5)
        print_result("获取完整配置", response)
        
        if response.status_code == 200:
            config = response.json().get("config", {})
            print(f"📊 配置统计:")
            print(f"   - 服务数量: {len(config.get('Services', []))}")
            print(f"   - 出站数量: {len(config.get('Outbounds', []))}")
            print(f"   - 日志级别: {config.get('Log', {}).get('Level', 'unknown')}")
            print(f"   - 默认出站: {config.get('Router', {}).get('DefaultOutbound', 'unknown')}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API连接失败: {e}")
        print("请确保:")
        print("1. ZBProxy管理API正在运行 (python main.py)")
        print("2. API服务运行在 http://localhost:8000")
        print("3. 防火墙没有阻止连接")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 ZBProxy配置更新测试脚本")
    print(f"🔗 API地址: {BASE_URL}")
    
    # 检查API连接性
    if not test_api_connectivity():
        print("\n❌ API连接失败，退出测试")
        sys.exit(1)
    
    print("\n⏳ 开始配置更新测试...")
    
    try:
        # 运行各种测试
        test_basic_config_updates()
        test_service_config_updates()
        test_outbound_config_updates()
        test_complex_config_updates()
        test_invalid_config_updates()
        
        print_separator("测试完成")
        print("✅ 所有测试已完成")
        print("📋 请查看上方的测试结果")
        print("💡 建议检查ZBProxy配置文件确认更改是否正确保存")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生异常: {e}")

def interactive_test():
    """交互式测试模式"""
    print_separator("交互式配置更新测试")
    
    while True:
        print("\n🔧 配置更新操作选项:")
        print("1. 获取完整配置")
        print("2. 获取指定路径配置值")
        print("3. 更新配置值")
        print("4. 运行预设测试")
        print("5. 退出")
        
        try:
            choice = input("\n请选择操作 (1-5): ").strip()
            
            if choice == "1":
                response = requests.get(f"{BASE_URL}/config")
                print_result("获取完整配置", response)
                
            elif choice == "2":
                path = input("请输入配置路径 (例: Log.Level): ").strip()
                if path:
                    get_config_value(path)
                    
            elif choice == "3":
                path = input("请输入配置路径 (例: Log.Level): ").strip()
                if not path:
                    continue
                    
                value_str = input("请输入新值: ").strip()
                if not value_str:
                    continue
                
                # 尝试解析值类型
                try:
                    # 尝试解析为JSON
                    if value_str.lower() in ['true', 'false']:
                        value = value_str.lower() == 'true'
                    elif value_str.isdigit():
                        value = int(value_str)
                    elif value_str.startswith('{') or value_str.startswith('['):
                        value = json.loads(value_str)
                    else:
                        value = value_str
                except json.JSONDecodeError:
                    value = value_str
                
                update_config(path, value)
                
            elif choice == "4":
                run_all_tests()
                break
                
            elif choice == "5":
                print("👋 退出测试")
                break
                
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n👋 用户退出")
            break
        except Exception as e:
            print(f"❌ 操作异常: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        run_all_tests()
