#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级分析模块
包含智能写作分析、学术规范检查、相似度检测等功能
"""

import re
import json
from typing import Dict, List, Any
from collections import Counter
import streamlit as st

class AdvancedAnalyzer:
    """高级分析器类"""
    
    def __init__(self):
        """初始化高级分析器"""
        self.academic_patterns = {
            'citation_formats': [
                r'\([^)]+\d{4}\)',  # (作者, 年份)
                r'\[[\d,]+\]',      # [1], [1,2]
            ],
            'reference_patterns': [
                r'参考文献', r'References', r'Bibliography'
            ]
        }
    
    def comprehensive_analysis(self, content: str) -> Dict[str, Any]:
        """综合文档分析"""
        if not content:
            return {"error": "内容为空"}
        
        return {
            "basic_stats": self._analyze_basic_stats(content),
            "structure_analysis": self._analyze_structure(content),
            "academic_quality": self._analyze_academic_quality(content),
            "writing_style": self._analyze_writing_style(content),
            "recommendations": self._generate_recommendations(content)
        }
    
    def _analyze_basic_stats(self, content: str) -> Dict[str, Any]:
        """基础统计分析"""
        words = content.split()
        sentences = re.split(r'[。！？.!?]', content)
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        return {
            "total_characters": len(content),
            "total_words": len(words),
            "total_sentences": len([s for s in sentences if s.strip()]),
            "total_paragraphs": len(paragraphs),
            "avg_sentence_length": len(words) / max(len([s for s in sentences if s.strip()]), 1),
            "reading_time_minutes": len(words) / 200
        }
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """结构分析"""
        lines = content.split('\n')
        structure = {
            "has_title": False,
            "has_abstract": False,
            "has_keywords": False,
            "has_introduction": False,
            "has_conclusion": False,
            "has_references": False,
            "structure_score": 0
        }
        
        # 检测各部分
        for line in lines:
            line_lower = line.lower()
            if '摘要' in line or 'abstract' in line_lower:
                structure["has_abstract"] = True
            if '关键词' in line or 'keywords' in line_lower:
                structure["has_keywords"] = True
            if '引言' in line or 'introduction' in line_lower:
                structure["has_introduction"] = True
            if '结论' in line or 'conclusion' in line_lower:
                structure["has_conclusion"] = True
            if '参考文献' in line or 'references' in line_lower:
                structure["has_references"] = True
        
        # 计算结构评分
        structure_score = 0
        if structure["has_abstract"]: structure_score += 20
        if structure["has_keywords"]: structure_score += 15
        if structure["has_introduction"]: structure_score += 20
        if structure["has_conclusion"]: structure_score += 20
        if structure["has_references"]: structure_score += 25
        
        structure["structure_score"] = structure_score
        
        return structure
    
    def _analyze_academic_quality(self, content: str) -> Dict[str, Any]:
        """学术质量分析"""
        quality = {
            "citation_count": 0,
            "formal_language_score": 0,
            "academic_terms_score": 0,
            "overall_quality_score": 0
        }
        
        # 统计引用数量
        for pattern in self.academic_patterns['citation_formats']:
            quality["citation_count"] += len(re.findall(pattern, content))
        
        # 正式语言评分
        formal_words = ['因此', '然而', '此外', '综上所述', '研究表明', '根据', '由于']
        formal_count = sum(1 for word in formal_words if word in content)
        quality["formal_language_score"] = min(formal_count * 10, 100)
        
        # 学术术语评分
        academic_terms = ['理论', '模型', '框架', '方法', '分析', '研究', '数据']
        term_count = sum(1 for term in academic_terms if term in content)
        quality["academic_terms_score"] = min(term_count * 15, 100)
        
        # 总体质量评分
        quality["overall_quality_score"] = (
            quality["formal_language_score"] * 0.4 +
            quality["academic_terms_score"] * 0.4 +
            min(quality["citation_count"] * 10, 20)
        )
        
        return quality
    
    def _analyze_writing_style(self, content: str) -> Dict[str, Any]:
        """写作风格分析"""
        style = {
            "sentence_complexity": 0,
            "vocabulary_diversity": 0,
            "tone_formality": 0,
            "clarity_score": 0
        }
        
        # 句子复杂度
        sentences = re.split(r'[。！？.!?]', content)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
        style["sentence_complexity"] = min(avg_sentence_length * 2, 100)
        
        # 词汇多样性
        words = content.split()
        unique_words = set(words)
        if words:
            style["vocabulary_diversity"] = min(len(unique_words) / len(words) * 100, 100)
        
        # 语调正式性
        informal_words = ['我', '你', '他', '她', '我们', '你们', '他们']
        informal_count = sum(1 for word in informal_words if word in content)
        style["tone_formality"] = max(100 - informal_count * 10, 0)
        
        # 清晰度评分
        long_sentences = sum(1 for s in sentences if len(s.split()) > 30)
        style["clarity_score"] = max(100 - long_sentences * 15, 0)
        
        return style
    
    def _generate_recommendations(self, content: str) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于内容长度的建议
        if len(content.split()) < 1000:
            recommendations.append("内容篇幅较短，建议增加更多详细内容")
        
        # 基于引用数量的建议
        citation_count = sum(len(re.findall(pattern, content)) for pattern in self.academic_patterns['citation_formats'])
        if citation_count < 3:
            recommendations.append("引用数量较少，建议增加相关文献引用")
        
        # 基于正式语言的建议
        formal_words = ['因此', '然而', '此外', '综上所述', '研究表明', '根据', '由于']
        formal_count = sum(1 for word in formal_words if word in content)
        if formal_count < 3:
            recommendations.append("建议使用更正式的学术语言，增加逻辑连接词")
        
        # 基于结构的建议
        if '摘要' not in content and 'Abstract' not in content:
            recommendations.append("建议添加摘要部分，简要概括研究内容")
        
        if '参考文献' not in content and 'References' not in content:
            recommendations.append("建议添加参考文献部分")
        
        return recommendations[:5]  # 最多返回5条建议

# 创建全局实例
advanced_analyzer = AdvancedAnalyzer()
