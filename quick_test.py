#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZBProxy配置更新快速测试脚本
"""

import requests
import json

# API配置
BASE_URL = "http://localhost:8000"

def test_config_updates():
    """快速配置更新测试"""
    print("🚀 ZBProxy配置更新快速测试")
    
    # 测试用例
    test_cases = [
        {
            "name": "修改日志级别为debug",
            "path": "Log.Level",
            "value": "debug"
        },
        {
            "name": "修改日志级别为info", 
            "path": "Log.Level",
            "value": "info"
        },
        {
            "name": "修改服务监听端口",
            "path": "Services.0.Listen",
            "value": 25566
        },
        {
            "name": "恢复服务监听端口",
            "path": "Services.0.Listen", 
            "value": 25565
        },
        {
            "name": "修改目标服务器地址",
            "path": "Outbounds.0.TargetAddress",
            "value": "mc.example.com"
        },
        {
            "name": "恢复目标服务器地址",
            "path": "Outbounds.0.TargetAddress",
            "value": "mc.hypixel.net1"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}: {test_case['name']}")
        
        # 先获取当前值
        try:
            get_response = requests.get(f"{BASE_URL}/config/{test_case['path']}")
            if get_response.status_code == 200:
                current_value = get_response.json().get("value")
                print(f"   当前值: {current_value}")
            else:
                print(f"   ❌ 获取当前值失败: {get_response.status_code}")
        except Exception as e:
            print(f"   ❌ 获取当前值异常: {e}")
        
        # 更新配置
        try:
            update_data = {
                "path": test_case["path"],
                "value": test_case["value"]
            }
            
            response = requests.put(
                f"{BASE_URL}/config", 
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"   ✅ 更新成功: {test_case['path']} = {test_case['value']}")
                else:
                    print(f"   ❌ 更新失败: {result.get('message', '未知错误')}")
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
                try:
                    error_detail = response.json().get("detail", response.text)
                    print(f"   错误详情: {error_detail}")
                except:
                    print(f"   响应内容: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ 更新异常: {e}")

if __name__ == "__main__":
    test_config_updates()
    print("\n🎉 测试完成！")
