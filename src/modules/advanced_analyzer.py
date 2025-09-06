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
        """综合文档分析 - 增强版"""
        if not content:
            return {"error": "内容为空"}
        
        return {
            "basic_stats": self._analyze_basic_stats(content),
            "structure_analysis": self._analyze_structure(content),
            "academic_quality": self._analyze_academic_quality(content),
            "writing_style": self._analyze_writing_style(content),
            "communication_analysis": self._analyze_communication_specialty(content),
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
    
    def _analyze_communication_specialty(self, content: str) -> Dict[str, Any]:
        """新闻传播学专业特色分析"""
        specialty = {
            "theory_application": 0,
            "method_appropriateness": 0,
            "industry_relevance": 0,
            "social_value": 0,
            "innovation_score": 0,
            "overall_specialty_score": 0
        }
        
        # 理论应用分析
        comm_theories = [
            '议程设置', '框架理论', '把关人', '意见领袖', '两级传播', '使用与满足',
            '培养理论', '沉默的螺旋', '知沟理论', '第三人效果', '媒介依赖',
            '社会认知理论', '社会学习理论', '创新扩散', '技术接受模型'
        ]
        theory_count = sum(1 for theory in comm_theories if theory in content)
        specialty["theory_application"] = min(theory_count * 20, 100)
        
        # 研究方法适当性
        comm_methods = [
            '内容分析', '问卷调查', '深度访谈', '焦点小组', '实验法', '案例研究',
            '民族志', '话语分析', '网络分析', '大数据分析', '文本挖掘'
        ]
        method_count = sum(1 for method in comm_methods if method in content)
        specialty["method_appropriateness"] = min(method_count * 25, 100)
        
        # 行业关联度
        industry_terms = [
            '新闻业', '媒体', '广播电视', '网络媒体', '社交媒体', '自媒体',
            '新闻生产', '新闻消费', '媒体融合', '数字化转型', '算法推荐',
            '假新闻', '信息茧房', '回音室', '过滤气泡'
        ]
        industry_count = sum(1 for term in industry_terms if term in content)
        specialty["industry_relevance"] = min(industry_count * 15, 100)
        
        # 社会价值
        social_terms = [
            '公共舆论', '民主参与', '社会监督', '信息传播', '知识普及',
            '文化传承', '社会整合', '舆论引导', '危机传播', '健康传播',
            '科学传播', '环境传播', '政治传播', '国际传播'
        ]
        social_count = sum(1 for term in social_terms if term in content)
        specialty["social_value"] = min(social_count * 20, 100)
        
        # 创新性评分
        innovation_indicators = [
            '新理论', '新方法', '新发现', '新视角', '新应用', '新模型',
            '首次', '突破', '创新', '原创', '前沿', '热点'
        ]
        innovation_count = sum(1 for indicator in innovation_indicators if indicator in content)
        specialty["innovation_score"] = min(innovation_count * 25, 100)
        
        # 总体专业特色评分
        specialty["overall_specialty_score"] = (
            specialty["theory_application"] * 0.25 +
            specialty["method_appropriateness"] * 0.25 +
            specialty["industry_relevance"] * 0.2 +
            specialty["social_value"] * 0.2 +
            specialty["innovation_score"] * 0.1
        )
        
        return specialty
    
    def _generate_recommendations(self, content: str) -> List[str]:
        """生成改进建议 - 增强版"""
        recommendations = []
        
        # 基于内容长度的建议
        word_count = len(content.split())
        if word_count < 1000:
            recommendations.append("内容篇幅较短，建议增加更多详细内容，包括理论分析、实证研究等")
        elif word_count > 10000:
            recommendations.append("内容篇幅较长，建议精简表达，突出核心观点")
        
        # 基于引用数量的建议
        citation_count = sum(len(re.findall(pattern, content)) for pattern in self.academic_patterns['citation_formats'])
        if citation_count < 5:
            recommendations.append("引用数量较少，建议增加相关文献引用，特别是近5年的重要文献")
        elif citation_count > 50:
            recommendations.append("引用数量较多，建议精选核心文献，避免过度引用")
        
        # 基于正式语言的建议
        formal_words = ['因此', '然而', '此外', '综上所述', '研究表明', '根据', '由于', '由此可见', '综上所述']
        formal_count = sum(1 for word in formal_words if word in content)
        if formal_count < 3:
            recommendations.append("建议使用更正式的学术语言，增加逻辑连接词，提升论证的严谨性")
        
        # 基于结构的建议
        if '摘要' not in content and 'Abstract' not in content:
            recommendations.append("建议添加摘要部分，简要概括研究目的、方法、结果和结论")
        
        if '关键词' not in content and 'Keywords' not in content:
            recommendations.append("建议添加关键词部分，便于文献检索和分类")
        
        if '参考文献' not in content and 'References' not in content:
            recommendations.append("建议添加参考文献部分，确保引用的完整性和规范性")
        
        # 基于新闻传播学专业特色的建议
        comm_terms = ['传播', '媒体', '新闻', '受众', '效果', '议程设置', '框架', '把关', '意见领袖']
        comm_count = sum(1 for term in comm_terms if term in content)
        if comm_count < 3:
            recommendations.append("建议增加更多新闻传播学专业术语和理论，体现学科特色")
        
        # 基于理论应用的建议
        theory_indicators = ['理论', '模型', '框架', '假设', '概念']
        theory_count = sum(1 for indicator in theory_indicators if indicator in content)
        if theory_count < 2:
            recommendations.append("建议加强理论分析，运用相关传播学理论支撑研究")
        
        # 基于研究方法的建议
        method_indicators = ['方法', '研究设计', '数据收集', '分析', '样本', '调查', '实验']
        method_count = sum(1 for indicator in method_indicators if indicator in content)
        if method_count < 2:
            recommendations.append("建议详细描述研究方法，包括研究设计、数据收集和分析方法")
        
        # 基于创新性的建议
        innovation_indicators = ['创新', '新发现', '首次', '突破', '贡献']
        innovation_count = sum(1 for indicator in innovation_indicators if indicator in content)
        if innovation_count < 1:
            recommendations.append("建议明确阐述研究的创新点和理论贡献")
        
        return recommendations[:8]  # 最多返回8条建议

# 创建全局实例
advanced_analyzer = AdvancedAnalyzer()
