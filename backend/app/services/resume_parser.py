from pypdf import PdfReader
import docx
import re
import nltk
from typing import Dict, List, Optional
import os

# Download NLTK data on first run
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')

class ResumeParser:
    def __init__(self):
        self.common_skills = {
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 
            'vue', 'node.js', 'express', 'django', 'flask', 'fastapi',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
            'git', 'agile', 'scrum', 'ci/cd', 'rest api', 'graphql',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch',
            'data science', 'pandas', 'numpy', 'scikit-learn', 'html',
            'css', 'tailwind', 'bootstrap', 'next.js', 'vue.js'
        }
    
    async def parse_file(self, file_path: str, file_type: str) -> Dict:
        """Main parser - routes to appropriate handler"""
        
        if file_type in ['pdf']:
            text = await self.extract_from_pdf(file_path)
        elif file_type in ['docx', 'doc']:
            text = await self.extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        parsed_data = await self.parse_text(text)
        return parsed_data
    
    async def extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            raise
        return text
    
    async def extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            raise
        return text
    
    async def parse_text(self, text: str) -> Dict:
        """Parse resume text and extract structured data"""
        
        name = self.extract_name(text)
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        skills = self.extract_skills(text)
        experience_years = self.extract_experience_years(text)
        education = self.extract_education(text)
        
        return {
            "candidate_name": name or "Unknown",
            "email": email or "unknown@email.com",
            "phone": phone,
            "skills": skills,
            "total_experience_years": experience_years,
            "education_level": education.get("level"),
            "education_field": education.get("field"),
            "summary": self.extract_summary(text),
            "raw_text": text
        }
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name using NLTK"""
        
        # Get first few lines
        lines = text.split('\n')[:5]
        
        for line in lines:
            line = line.strip()
            # Name is usually 2-4 words at the top
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if it looks like a name (starts with capitals)
                if all(w[0].isupper() for w in words if w):
                    return line
        
        # Fallback: use NLTK NER
        try:
            from nltk import ne_chunk, pos_tag, word_tokenize
            tokens = word_tokenize(text[:500])
            pos_tags = pos_tag(tokens)
            chunks = ne_chunk(pos_tags)
            
            for chunk in chunks:
                if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                    return ' '.join(c[0] for c in chunk)
        except:
            pass
        
        return None
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        pattern = r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Also look for skills section
        skills_section_pattern = r'(?:skills|technical skills|core competencies)[\s:]*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\n[A-Z]|$)'
        skills_match = re.search(skills_section_pattern, text, re.IGNORECASE)
        
        if skills_match:
            skills_text = skills_match.group(1)
            additional_skills = re.split(r'[,;•\n\t]', skills_text)
            for skill in additional_skills:
                skill = skill.strip()
                if skill and len(skill) > 2 and len(skill) < 30:
                    found_skills.append(skill.title())
        
        return list(set(found_skills))[:20]  # Limit to 20 skills
    
    def extract_experience_years(self, text: str) -> float:
        """Extract years of experience"""
        
        # Pattern 1: "5 years", "5+ years"
        pattern = r'(\d+)[\+\-\s]*(?:years?|yrs?)'
        matches = re.findall(pattern, text.lower())
        
        if matches:
            years = [int(m) for m in matches]
            return max(years)
        
        # Pattern 2: Date ranges "2020-2023"
        date_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'
        date_matches = re.findall(date_pattern, text.lower())
        
        if date_matches:
            total_years = 0
            for start, end in date_matches:
                start_year = int(start)
                end_year = 2024 if end in ['present', 'current'] else int(end)
                years = end_year - start_year
                if 0 <= years <= 50:  # Sanity check
                    total_years += years
            return float(total_years)
        
        return 0.0
    
    def extract_education(self, text: str) -> Dict:
        """Extract education information"""
        education = {"level": None, "field": None}
        text_lower = text.lower()
        
        # Check for degree level
        if "phd" in text_lower or "ph.d" in text_lower or "doctorate" in text_lower:
            education["level"] = "PhD"
        elif "master" in text_lower or "m.s." in text_lower or "mba" in text_lower or "m.a." in text_lower:
            education["level"] = "Master's"
        elif "bachelor" in text_lower or "b.s." in text_lower or "b.a." in text_lower or "b.tech" in text_lower:
            education["level"] = "Bachelor's"
        
        # Check for field
        fields = [
            "computer science", "engineering", "business", "mathematics", 
            "data science", "information technology", "software engineering",
            "computer engineering", "electrical engineering", "statistics"
        ]
        
        for field in fields:
            if field in text_lower:
                education["field"] = field.title()
                break
        
        return education
    
    def extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary"""
        
        # Look for summary section
        summary_pattern = r'(?:summary|profile|objective|about)[\s:]*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\n[A-Z]{2,}|$)'
        match = re.search(summary_pattern, text, re.IGNORECASE)
        
        if match:
            summary = match.group(1).strip()
            # Clean up
            summary = re.sub(r'\s+', ' ', summary)
            return summary[:500]
        
        # Fallback: use first substantial paragraph
        paragraphs = text.split('\n\n')
        for para in paragraphs[1:4]:  # Skip first (usually name)
            para = para.strip()
            if len(para) > 100:  # Substantial paragraph
                return para[:500]
        
        return None
