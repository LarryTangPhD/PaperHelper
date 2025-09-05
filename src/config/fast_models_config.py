#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速模型配置文件
提供多种模型选择，优化响应速度
"""

import os
from typing import Dict, Any

class FastModelsConfig:
    """快速模型配置类"""
    
    def __init__(self):
        """初始化模型配置"""
        self.models = {
            # 1. 本地模型（最快）
            "local_llama": {
                "name": "Llama-2-7B-Chat",
                "type": "local",
                "speed": "极快",
                "cost": "免费",
                "setup": "需要本地部署",
                "api_base": "http://localhost:11434/v1",
                "model_name": "llama2:7b-chat",
                "temperature": 0.7
            },
            
            # 2. 开源API模型（较快）
            "openai_gpt35": {
                "name": "GPT-3.5-Turbo",
                "type": "api",
                "speed": "快",
                "cost": "低",
                "setup": "需要OpenAI API Key",
                "api_base": "https://api.openai.com/v1",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7
            },
            
            "anthropic_claude": {
                "name": "Claude-3-Haiku",
                "type": "api",
                "speed": "快",
                "cost": "低",
                "setup": "需要Anthropic API Key",
                "api_base": "https://api.anthropic.com",
                "model_name": "claude-3-haiku-20240307",
                "temperature": 0.7
            },
            
            # 3. 国内模型（较快）
            "baichuan": {
                "name": "百川大模型",
                "type": "api",
                "speed": "快",
                "cost": "低",
                "setup": "需要百川API Key",
                "api_base": "https://api.baichuan-ai.com/v1",
                "model_name": "Baichuan2-Turbo",
                "temperature": 0.7
            },
            
            "qwen": {
                "name": "通义千问-Turbo",
                "type": "api",
                "speed": "极快",
                "cost": "低",
                "setup": "需要阿里云API Key",
                "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model_name": "qwen-turbo",
                "temperature": 0.3,
                "max_tokens": 1500,
                "timeout": 30
            },
            
            "qwen_plus": {
                "name": "通义千问-Plus",
                "type": "api",
                "speed": "快",
                "cost": "中",
                "setup": "需要阿里云API Key",
                "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model_name": "qwen-plus",
                "temperature": 0.3,
                "max_tokens": 2000,
                "timeout": 45
            },
            
            # 4. 轻量级模型（最快）
            "phi": {
                "name": "Microsoft Phi-2",
                "type": "local",
                "speed": "极快",
                "cost": "免费",
                "setup": "需要本地部署",
                "api_base": "http://localhost:11434/v1",
                "model_name": "phi:2.7b",
                "temperature": 0.7
            },
            
            "gemma": {
                "name": "Google Gemma-2B",
                "type": "local",
                "speed": "极快",
                "cost": "免费",
                "setup": "需要本地部署",
                "api_base": "http://localhost:11434/v1",
                "model_name": "gemma:2b",
                "temperature": 0.7
            }
        }
        
        # 默认模型配置 - 使用通义千问
        self.default_model = "qwen_plus"
        
    def get_model_config(self, model_key: str = None) -> Dict[str, Any]:
        """获取模型配置"""
        if model_key is None:
            model_key = self.default_model
        
        if model_key in self.models:
            return self.models[model_key]
        else:
            return self.models[self.default_model]
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """获取所有可用模型"""
        return self.models
    
    def get_fastest_models(self) -> Dict[str, Dict[str, Any]]:
        """获取最快的模型"""
        fast_models = {}
        for key, config in self.models.items():
            if config["speed"] in ["极快", "快"]:
                fast_models[key] = config
        return fast_models
    
    def get_free_models(self) -> Dict[str, Dict[str, Any]]:
        """获取免费模型"""
        free_models = {}
        for key, config in self.models.items():
            if config["cost"] == "免费":
                free_models[key] = config
        return free_models

# 创建全局实例
fast_models_config = FastModelsConfig()
