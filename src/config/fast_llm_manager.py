#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速模型管理器
支持多种模型切换，优化响应速度
"""

import os
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama
from src.config.fast_models_config import fast_models_config

class FastLLMManager:
    """快速模型管理器"""
    
    def __init__(self):
        """初始化模型管理器"""
        self.current_model = None
        self.model_config = None
        self.llm_instance = None
        
    def switch_model(self, model_key: str) -> Dict[str, Any]:
        """切换模型"""
        try:
            # 获取模型配置
            self.model_config = fast_models_config.get_model_config(model_key)
            self.current_model = model_key
            
            # 根据模型类型创建实例
            if self.model_config["type"] == "local":
                self.llm_instance = self._create_local_model()
            elif self.model_config["type"] == "api":
                self.llm_instance = self._create_api_model()
            else:
                raise ValueError(f"不支持的模型类型: {self.model_config['type']}")
            
            return {
                "success": True,
                "model": model_key,
                "config": self.model_config,
                "message": f"成功切换到 {self.model_config['name']}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"切换模型失败: {str(e)}"
            }
    
    def _create_local_model(self):
        """创建本地模型实例"""
        if self.current_model in ["local_llama", "phi", "gemma"]:
            # 使用Ollama运行本地模型
            return Ollama(
                model=self.model_config["model_name"],
                temperature=self.model_config["temperature"]
            )
        else:
            raise ValueError(f"不支持的本地模型: {self.current_model}")
    
    def _create_api_model(self):
        """创建API模型实例 - 优化版配置"""
        if self.current_model == "openai_gpt35":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("未设置OPENAI_API_KEY环境变量")
            
            return ChatOpenAI(
                model=self.model_config["model_name"],
                temperature=self.model_config["temperature"],
                api_key=api_key,
                max_tokens=self.model_config.get("max_tokens", 1500),
                timeout=self.model_config.get("timeout", 30),
                request_timeout=self.model_config.get("timeout", 30)
            )
            
        elif self.current_model == "anthropic_claude":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("未设置ANTHROPIC_API_KEY环境变量")
            
            return ChatAnthropic(
                model=self.model_config["model_name"],
                temperature=self.model_config["temperature"],
                api_key=api_key
            )
            
        elif self.current_model == "baichuan":
            api_key = os.getenv("BAICHUAN_API_KEY")
            if not api_key:
                raise ValueError("未设置BAICHUAN_API_KEY环境变量")
            
            return ChatOpenAI(
                model=self.model_config["model_name"],
                temperature=self.model_config["temperature"],
                api_key=api_key,
                base_url=self.model_config["api_base"]
            )
            
        elif self.current_model == "qwen":
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise ValueError("未设置DASHSCOPE_API_KEY环境变量")
            
            return ChatOpenAI(
                model=self.model_config["model_name"],
                temperature=self.model_config["temperature"],
                api_key=api_key,
                base_url=self.model_config["api_base"],
                max_tokens=self.model_config.get("max_tokens", 1500),
                timeout=self.model_config.get("timeout", 30),
                request_timeout=self.model_config.get("timeout", 30)
            )
            
        elif self.current_model == "qwen_plus":
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise ValueError("未设置DASHSCOPE_API_KEY环境变量")
            
            return ChatOpenAI(
                model=self.model_config["model_name"],
                temperature=self.model_config["temperature"],
                api_key=api_key,
                base_url=self.model_config["api_base"],
                max_tokens=self.model_config.get("max_tokens", 2000),
                timeout=self.model_config.get("timeout", 45),
                request_timeout=self.model_config.get("timeout", 45)
            )
            
        else:
            raise ValueError(f"不支持的API模型: {self.current_model}")
    
    def get_llm(self, temperature: float = None) -> Any:
        """获取LLM实例"""
        if self.llm_instance is None:
            # 使用默认模型
            self.switch_model(fast_models_config.default_model)
        
        # 如果指定了temperature，创建新的实例
        if temperature is not None and temperature != self.model_config["temperature"]:
            if self.model_config["type"] == "local":
                return Ollama(
                    model=self.model_config["model_name"],
                    temperature=temperature
                )
            elif self.model_config["type"] == "api":
                if self.current_model == "openai_gpt35":
                    return ChatOpenAI(
                        model=self.model_config["model_name"],
                        temperature=temperature,
                        api_key=os.getenv("OPENAI_API_KEY")
                    )
                elif self.current_model == "anthropic_claude":
                    return ChatAnthropic(
                        model=self.model_config["model_name"],
                        temperature=temperature,
                        api_key=os.getenv("ANTHROPIC_API_KEY")
                    )
                # 其他模型类似...
        
        return self.llm_instance
    
    def get_current_model_info(self) -> Dict[str, Any]:
        """获取当前模型信息"""
        if self.model_config is None:
            return {"error": "未选择模型"}
        
        return {
            "model": self.current_model,
            "name": self.model_config["name"],
            "type": self.model_config["type"],
            "speed": self.model_config["speed"],
            "cost": self.model_config["cost"],
            "temperature": self.model_config["temperature"]
        }
    
    def test_model_connection(self) -> Dict[str, Any]:
        """测试模型连接"""
        try:
            llm = self.get_llm()
            # 发送简单测试请求
            response = llm.invoke("你好")
            
            return {
                "success": True,
                "response": str(response),
                "model": self.current_model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"模型连接测试失败: {str(e)}"
            }

# 创建全局实例
fast_llm_manager = FastLLMManager()
