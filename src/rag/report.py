import logging
import os
from typing import Dict, List, Optional, Any
from src.utils.config import get_config
from .knowledge_base import KnowledgeBase

logger = logging.getLogger("badminton_cv.rag")

class ReportGenerator:
    def __init__(self, knowledge_base: KnowledgeBase, config: Optional[Dict] = None):
        self.kb = knowledge_base
        self._config_config = config if config else get_config()
        self.config = self._config_config.config if hasattr(self._config_config, 'config') else self._config_config.config if hasattr(self._config_config, 'config') else get_config().config
        
        self.llm_model = self.config.get('rag.llm_model', 'gpt-4')
        # Check if we should mock (if no API key)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.use_mock = self.api_key is None
        
        if self.use_mock:
            logger.info("No OPENAI_API_KEY found. Using Mock LLM.")

    def generate_report(self, match_metrics: Dict[str, Any], events: List[Dict[str, Any]]) -> str:
        """
        Generate a coaching report.
        """
        # 1. Analyze metrics to find weaknesses
        context_queries = self._analyze_weaknesses(match_metrics)
        
        # 2. Retrieve knowledge
        retrieved_docs = []
        for q in context_queries:
            docs = self.kb.query(q, n_results=2)
            retrieved_docs.extend(docs)
            
        # Deduplicate
        seen = set()
        unique_docs = []
        for d in retrieved_docs:
            if d['text'] not in seen:
                unique_docs.append(d)
                seen.add(d['text'])
                
        # 3. Construct Prompt
        prompt = self._construct_prompt(match_metrics, unique_docs)
        
        # 4. Call LLM
        return self._call_llm(prompt)

    def _analyze_weaknesses(self, metrics: Dict[str, Any]) -> List[str]:
        """Derive search queries from metrics."""
        queries = []
        # Example logic
        if 'shuttle_max_speed_kmh' in metrics and metrics['shuttle_max_speed_kmh'] < 150:
            queries.append("how to improve smash power badminton")
            
        # Check distance
        for pid, p_stats in metrics.get('players', {}).items():
            if p_stats.get('total_distance_m', 0) < 500: # Low movement
                queries.append("badminton footwork drills for agility")
                
        if not queries:
            queries.append("general badminton strategy")
            
        return queries

    def _construct_prompt(self, metrics: Dict[str, Any], docs: List[Dict[str, Any]]) -> str:
        context_str = "\n".join([f"- {d['text']}" for d in docs])
        
        prompt = f"""
        You are an expert Badminton Coach. Generate a performance report based on the following match data.
        
        Match Data:
        - Max Shuttle Speed: {metrics.get('shuttle_max_speed_kmh', 0):.1f} km/h
        - Player Stats: {metrics.get('players', {})}
        
        Coaching Knowledge Context:
        {context_str}
        
        Please provide:
        1. Performance Summary
        2. Key Strengths
        3. Areas for Improvement
        4. Recommended Drills (reference the context)
        """
        return prompt

    def _call_llm(self, prompt: str) -> str:
        # Load env vars if not loaded
        from dotenv import load_dotenv
        load_dotenv()
        
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=google_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                return response.text
            except ImportError:
                 logger.error("google-generativeai not installed.")
            except Exception as e:
                 logger.error(f"Gemini API call failed: {e}")
                 
        if self.use_mock:
            return self._mock_llm_response(prompt)
            
        return "Error: LLM call failed and no mock fallback enabled."

    def _mock_llm_response(self, prompt: str) -> str:
        return f"""
        [MOCK LLM REPORT]
        
        # Badminton Match Analysis
        
        ## Performance Summary
        The player showed good consistency but lacked finishing power. Max speed was relatively low.
        
        ## Areas for Improvement
        - Smash Power: Your max speed indicates a need for better technique.
        - Footwork: Coverage suggests efficient but passive movement.
        
        ## Recommended Drills
        (Based on retrieved context)
        - Practice the drills mentioned in the context to improve power and agility.
        """
