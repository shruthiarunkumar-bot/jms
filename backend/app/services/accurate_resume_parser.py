from pypdf import PdfReader
import docx
import re
import nltk
from typing import Dict, List, Optional
import os

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)

class AccurateResumeParser:
    """Enhanced resume parser with high accuracy"""
    
    def __init__(self):
        # Expanded skills database
        self.skills_database = {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
            'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl',
            
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'vue.js', 'next.js', 'nuxt',
            'svelte', 'jquery', 'bootstrap', 'tailwind', 'sass', 'less',
            
            # Backend Frameworks
            'node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 'spring boot',
            '.net', 'asp.net', 'laravel', 'rails', 'ruby on rails',
            
            # Mobile
            'react native', 'flutter', 'ios', 'android', 'xamarin', 'ionic',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
            'jenkins', 'terraform', 'ansible', 'gitlab', 'github actions', 'circleci',
            'ci/cd', 'heroku', 'netlify', 'vercel',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'dynamodb', 'firebase', 'oracle', 'sql server', 'sqlite',
            
            # Data Science & ML
            'machine learning', 'deep learning', 'artificial intelligence', 'ai',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'data science', 'data analysis', 'tableau', 'power bi', 'spark',
            
            # Testing
            'jest', 'mocha', 'pytest', 'junit', 'selenium', 'cypress', 'testing',
            'unit testing', 'integration testing', 'tdd',
            
            # Tools & Others
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack',
            'agile', 'scrum', 'kanban', 'rest api', 'graphql', 'microservices',
            'api', 'linux', 'unix', 'bash', 'shell scripting'
        }
    
    async def parse_file(self, file_path: str, file_type: str) -> Dict:
        """Parse resume file with high accuracy"""
        
        if file_type == 'pdf':
            text = await self.extract_from_pdf(file_path)
        elif file_type in ['docx', 'doc']:
            text = await self.extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        parsed_data = await self.parse_text(text)
        parsed_data['raw_text'] = text
        
        return parsed_data
    
    async def extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF with better handling"""
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        if not text.strip():
            raise Exception("Could not extract text from PDF. File may be image-based or corrupted.")
        
        return text
    
    async def extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Also extract from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + "\n"
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        
        if not text.strip():
            raise Exception("Could not extract text from DOCX. File may be empty or corrupted.")
        
        return text
    
    async def parse_text(self, text: str) -> Dict:
        """Parse resume text with high accuracy"""
        
        # Clean text
        text = self.clean_text(text)
        
        # Extract all fields
        result = {
            "candidate_name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "location": self.extract_location(text),
            "linkedin": self.extract_linkedin(text),
            "github": self.extract_github(text),
            "skills": self.extract_skills(text),
            "total_experience_years": self.extract_experience_years(text),
            "current_title": self.extract_current_title(text),
            "education_level": self.extract_education_level(text),
            "education_field": self.extract_education_field(text),
            "summary": self.extract_summary(text),
            "certifications": self.extract_certifications(text),
            "companies": self.extract_companies(text)
        }
        
        # Set defaults for required fields
        if not result["candidate_name"]:
            result["candidate_name"] = "Unknown Candidate"
        if not result["email"]:
            result["email"] = "noemail@provided.com"
        
        return result
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s@.+\-():/]', ' ', text)
        return text.strip()
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name with high accuracy"""
        
        lines = text.split('\n')
        
        # Method 1: First non-empty line (most common)
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) >= 2 and len(line.split()) <= 5:
                # Check if it looks like a name
                words = line.split()
                if all(word[0].isupper() for word in words if word):
                    # Not a common header
                    if line.lower() not in ['curriculum vitae', 'resume', 'cv']:
                        return line
        
        # Method 2: Look for "Name:" pattern
        name_pattern = r'(?:name|full name)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        match = re.search(name_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email with validation"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        
        # Filter out common false positives
        valid_emails = [
            email for email in matches 
            if not email.startswith('http') and '@' in email
        ]
        
        return valid_emails[0] if valid_emails else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        patterns = [
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US
            r'\+\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}',  # International
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    def extract_location(self, text: str) -> Optional[str]:
        """Extract location"""
        # Common location patterns
        pattern = r'(?:Location|Address|Based in)[:\s]+([A-Z][a-z]+(?:,?\s+[A-Z]{2})?(?:,?\s+\d{5})?)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # City, State pattern
        pattern2 = r'\b([A-Z][a-z]+,\s*[A-Z]{2})\b'
        match2 = re.search(pattern2, text)
        if match2:
            return match2.group(1)
        
        return None
    
    def extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL"""
        pattern = r'(?:linkedin\.com/in/|linkedin\.com/profile/)[\w-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"https://{match.group(0)}" if not match.group(0).startswith('http') else match.group(0)
        return None
    
    def extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL"""
        pattern = r'(?:github\.com/)[\w-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"https://{match.group(0)}" if not match.group(0).startswith('http') else match.group(0)
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills with high accuracy"""
        text_lower = text.lower()
        found_skills = set()
        
        # Method 1: Direct matching from database
        for skill in self.skills_database:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        # Method 2: Extract from Skills section
        skills_section = self.extract_section(text, ['skills', 'technical skills', 'core competencies'])
        if skills_section:
            # Split by common delimiters
            skill_items = re.split(r'[,;•\n\t|]', skills_section)
            for item in skill_items:
                item = item.strip().lower()
                if 2 < len(item) < 30 and item in self.skills_database:
                    found_skills.add(item)
        
        # Convert to title case for display
        return sorted([skill.title() for skill in found_skills])
    
    def extract_section(self, text: str, headers: List[str]) -> Optional[str]:
        """Extract specific section from resume"""
        for header in headers:
            pattern = f'(?:{header})[:\s]*([^\n]+(?:\n(?!\n|[A-Z]{{2,}}).*)*)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_experience_years(self, text: str) -> float:
        """Calculate total years of experience"""
        
        # Method 1: Explicit years statement
        pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)'
        matches = re.findall(pattern, text.lower())
        if matches:
            years = [int(m) for m in matches]
            return max(years)
        
        # Method 2: Calculate from date ranges
        date_pattern = r'(\d{4})\s*[-–—]\s*(\d{4}|present|current)'
        date_matches = re.findall(date_pattern, text.lower())
        
        if date_matches:
            total_years = 0
            for start, end in date_matches:
                try:
                    start_year = int(start)
                    end_year = 2024 if end in ['present', 'current'] else int(end)
                    years = end_year - start_year
                    if 0 <= years <= 50:  # Sanity check
                        total_years += years
                except:
                    continue
            
            return float(total_years) if total_years > 0 else 0.0
        
        return 0.0
    
    def extract_current_title(self, text: str) -> Optional[str]:
        """Extract current job title"""
        
        # Look for recent job (with "present" or "current")
        pattern = r'([A-Z][a-z\s]+(?:Engineer|Developer|Manager|Analyst|Scientist|Designer|Consultant|Architect))\s+.*?(?:present|current)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Look in summary section
        summary_section = self.extract_section(text, ['summary', 'objective', 'profile'])
        if summary_section:
            title_pattern = r'(?:as|am)\s+a\s+([A-Z][a-z\s]+(?:Engineer|Developer|Manager|Analyst|Scientist|Designer))'
            match = re.search(title_pattern, summary_section, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_education_level(self, text: str) -> Optional[str]:
        """Extract highest education level"""
        text_lower = text.lower()
        
        if any(x in text_lower for x in ['phd', 'ph.d', 'doctorate', 'doctoral']):
            return "PhD"
        elif any(x in text_lower for x in ['master', "master's", 'm.s.', 'm.a.', 'mba', 'm.tech']):
            return "Master's"
        elif any(x in text_lower for x in ['bachelor', "bachelor's", 'b.s.', 'b.a.', 'b.tech', 'b.e.']):
            return "Bachelor's"
        elif any(x in text_lower for x in ['associate', 'diploma']):
            return "Associate's"
        
        return None
    
    def extract_education_field(self, text: str) -> Optional[str]:
        """Extract field of study"""
        fields = [
            'computer science', 'computer engineering', 'software engineering',
            'information technology', 'data science', 'artificial intelligence',
            'electrical engineering', 'mechanical engineering', 'business',
            'mathematics', 'statistics', 'physics', 'chemistry', 'biology',
            'economics', 'finance', 'marketing', 'management'
        ]
        
        text_lower = text.lower()
        for field in fields:
            if field in text_lower:
                return field.title()
        
        return None
    
    def extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary"""
        
        summary_section = self.extract_section(
            text, 
            ['summary', 'professional summary', 'profile', 'objective', 'about']
        )
        
        if summary_section:
            # Clean and limit length
            summary = re.sub(r'\s+', ' ', summary_section).strip()
            return summary[:500]
        
        # Fallback: Use first substantial paragraph after name
        paragraphs = text.split('\n\n')
        for para in paragraphs[1:4]:
            para = para.strip()
            if len(para) > 100:
                return para[:500]
        
        return None
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_section = self.extract_section(
            text,
            ['certifications', 'certificates', 'licenses']
        )
        
        if cert_section:
            certs = re.split(r'[,;\n•]', cert_section)
            return [cert.strip() for cert in certs if cert.strip() and len(cert.strip()) > 3][:10]
        
        return []
    
    def extract_companies(self, text: str) -> List[str]:
        """Extract previous companies"""
        
        # Look for company names after job titles
        pattern = r'(?:at|@)\s+([A-Z][A-Za-z\s&]+(?:Inc|LLC|Corp|Ltd)?)'
        matches = re.findall(pattern, text)
        
        companies = []
        for match in matches:
            company = match.strip()
            if 3 < len(company) < 50:
                companies.append(company)
        
        return list(set(companies))[:5]
