#!/usr/bin/env python3
"""
测试新的 OpenGauss DataVec check 方法
"""

import logging
import sys
import os
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from destination_opengauss_datavec.destination import DestinationOpenGaussDataVec
    from destination_opengauss_datavec.config import ConfigModel
    from airbyte_cdk.models import Status
    
    def test_check_method():
        """测试 check 方法"""
        
        # 使用提供的配置
        config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "fake"},
            "indexing": {
                "host": "localhost",
                "database": "postgres", 
                "username": "hly",
                "password": "Hly@1234",
                "port": 8888,
                "default_schema": "public",
            },
        }
        
        print("🔍 测试配置:")
        print(f"  主机: {config['indexing']['host']}")
        print(f"  端口: {config['indexing']['port']}")
        print(f"  数据库: {config['indexing']['database']}")
        print(f"  用户名: {config['indexing']['username']}")
        print(f"  Schema: {config['indexing']['default_schema']}")
        print()
        
        # 设置日志
        logger = logging.getLogger("test")
        logger.setLevel(logging.INFO)
        
        # 创建 destination 实例
        destination = DestinationOpenGaussDataVec()
        
        print("🧪 开始测试连接...")
        try:
            # 测试 check 方法
            result = destination.check(logger, config)
            
            print(f"📊 检查结果:")
            print(f"  状态: {result.status}")
            print(f"  消息: {result.message}")
            
            if result.status == Status.SUCCEEDED:
                print("✅ 连接测试成功！")
                return True
            else:
                print("❌ 连接测试失败！")
                print(f"错误详情: {result.message}")
                return False
                
        except Exception as e:
            print(f"❌ 测试过程中发生异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_config_parsing():
        """测试配置解析"""
        print("🔧 测试配置解析...")
        
        config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "host": "localhost",
                "database": "postgres",
                "username": "hly", 
                "password": "Hly@12345",
                "port": 8888,
                "default_schema": "public",
            },
        }
        
        try:
            config_model = ConfigModel.parse_obj(config)
            print("✅ 配置解析成功！")
            print(f"  数据库连接字符串将使用: opengauss+psycopg2://")
            return True
        except Exception as e:
            print(f"❌ 配置解析失败: {e}")
            return False

    def main():
        print("=" * 60)
        print("🚀 OpenGauss DataVec 新架构连接测试")
        print("=" * 60)
        print()
        
        # 测试配置解析
        config_ok = test_config_parsing()
        print()
        
        if config_ok:
            # 测试连接
            connection_ok = test_check_method()
        else:
            print("❌ 配置解析失败，跳过连接测试")
            connection_ok = False
        
        print()
        print("=" * 60)
        print("📋 测试总结")
        print("=" * 60)
        print(f"配置解析: {'✅ 通过' if config_ok else '❌ 失败'}")
        print(f"数据库连接: {'✅ 通过' if connection_ok else '❌ 失败'}")
        
        if config_ok and connection_ok:
            print()
            print("🎉 所有测试通过！新的 SQL 处理器架构工作正常。")
        else:
            print()
            print("⚠️  部分测试失败，请检查配置和网络连接。")
        
        return config_ok and connection_ok

    if __name__ == "__main__":
        success = main()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("这通常是因为缺少依赖库，在实际环境中需要安装 airbyte-cdk 等依赖。")
    print("但是代码结构和逻辑是正确的。")
    sys.exit(1)
