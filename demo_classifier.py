#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Mode Classifier for Khmer News Classification
=================================================

This module provides a simplified demonstration mode that can work without
the full FastText model for basic text classification demonstration.

Author: FYP Research Team
Version: 1.0.0
Date: June 14, 2025
License: Academic Research Use
"""

import numpy as np
from typing import Dict, List, Any
import re
import unicodedata

class DemoClassifier:
    """Demo classifier that works without FastText model"""
    
    def __init__(self):
        """Initialize the demo classifier with keyword-based rules"""
        self.categories = ["economic", "environment", "health", "politic", "sport", "technology"]
        
        # Simple keyword-based classification rules
        self.keywords = {
            "economic": [
                "ជំនួញ", "លុយ", "ប្រាក់", "សេដ្ឋកិច្ច", "ធនាគារ", "ពាណិជ្ជកម្ម", 
                "តម្លៃ", "ទីផ្សារ", "វិនិយោគ", "ភាគហ៊ុន", "គ្រុប", "ហ្វាំង"
            ],
            "environment": [
                "បរិស្ថាន", "ព្រៃឈើ", "ធម្មជាតិ", "ដី", "ទឹក", "អាកាស", 
                "មហាសមុទ្រ", "កាត់ព្រៃ", "ប្រើប្រាស់", "ការពារ", "ជីវចម្រុះ"
            ],
            "health": [
                "សុខភាព", "មន្ទីរពេទ្យ", "វេជ្ជបណ្ឌិត", "ជំងឺ", "ថ្នាំ", "ព្យាបាល", 
                "គ្រុនឈាម", "អេដស៍", "ស្ត្រី", "កុមារ", "ការពារ", "របុសរបួស"
            ],
            "politic": [
                "នយោបាយ", "រដ្ឋាភិបាល", "ព្រឹទ្ធសភា", "បោះឆ្នោត", "ព្រះមហាក្សត្រ", 
                "មន្ត្រី", "ក្រុម", "គណបក្ស", "លោកនាយករដ្ឋមន្ត្រី", "ច្បាប់", "ជាតិ"
            ],
            "sport": [
                "កីឡា", "កីឡាករ", "ប្រកួត", "ម៉ីត", "បាល់ទាត់", "វាយកូន", 
                "ហែលទឹក", "ម៉ារ៉ាតុង", "ពាន", "ជើងឯក", "ទទួលបាន"
            ],
            "technology": [
                "បច្ចេកវិទ្យា", "កុំព្យូទ័រ", "ទូរស័ព្ទ", "អ៊ីនធឺណេត", "កម្មវិធី", 
                "ទិន្នន័យ", "ឌីជីថល", "ថាមពល", "បច្ចេកទេស", "ការងារ", "ពត៌មាន"
            ]
        }
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """Classify text using simple keyword matching"""
        # Clean and normalize text
        text = self._clean_text(text)
        words = text.split()
        
        # Count keyword matches for each category
        scores = {}
        for category, keywords in self.keywords.items():
            score = 0
            for keyword in keywords:
                score += text.count(keyword)
            scores[category] = score
        
        # Determine prediction
        if max(scores.values()) == 0:
            # No keywords found, return random category
            prediction = "economic"  # Default
            confidence = 0.3
        else:
            prediction = max(scores, key=scores.get)
            total_score = sum(scores.values())
            confidence = scores[prediction] / total_score if total_score > 0 else 0.3
        
        # Generate confidence scores for all categories
        confidence_dict = {}
        total = sum(scores.values()) if sum(scores.values()) > 0 else len(self.categories)
        
        for category in self.categories:
            if total > 0:
                confidence_dict[category] = max(0.1, scores.get(category, 0) / total)
            else:
                confidence_dict[category] = 1.0 / len(self.categories)
        
        # Normalize confidence scores to sum to 1
        total_conf = sum(confidence_dict.values())
        if total_conf > 0:
            confidence_dict = {k: v/total_conf for k, v in confidence_dict.items()}
        
        return {
            'prediction': prediction,
            'confidence': confidence_dict,
            'word_matches': scores,
            'demo_mode': True
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize Khmer text"""
        if not text:
            return ""
        
        # Unicode normalization
        text = unicodedata.normalize('NFC', text)
        
        # Remove unwanted characters
        text = re.sub(r'[^\u1780-\u17FF\u19E0-\u19FF\u1A00-\u1A1F\s]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text.lower()
    
    def get_demo_info(self) -> Dict[str, Any]:
        """Get information about demo mode"""
        return {
            'mode': 'Demo Mode',
            'description': 'Simplified keyword-based classification',
            'categories': self.categories,
            'limitations': [
                'Uses simple keyword matching instead of machine learning',
                'Lower accuracy compared to full model',
                'Good for demonstration purposes only'
            ],
            'keyword_count': sum(len(keywords) for keywords in self.keywords.values())
        }
