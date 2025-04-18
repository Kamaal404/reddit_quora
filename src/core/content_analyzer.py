"""
Content Analyzer for determining relevance of social media posts to products.
"""

import logging
import os
import re
import pickle
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set, Optional

# Import product and niche configurations
from src.config.products import PRODUCTS
from src.config.niches import NICHES

# Import spaCy conditionally
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    nltk = None
    NLTK_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """
    Analyzes content for relevance to QiLifeStore products.
    
    This class determines how relevant a post or question is to
    QiLifeStore products and identifies which products match best.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ContentAnalyzer.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.nlp_config = config.get("nlp", {})
        
        # Load products from dedicated module
        self.products_config = PRODUCTS
        logger.info(f"Loaded {len(self.products_config)} products from products module")
        
        # Load niches from dedicated module
        self.niches_config = NICHES
        logger.info(f"Loaded {len(self.niches_config)} niches from niches module")
        
        # Check if niches are enabled in the configuration
        self.niches_enabled = config.get("general", {}).get("niches_enabled", False)
        
        # Force the model type to fallback if spaCy is not available
        if not SPACY_AVAILABLE:
            self.model_type = "fallback"
            logger.warning("spaCy not available, using fallback keyword-based approach")
        else:
            self.model_type = self.nlp_config.get("relevance_model", "fallback")
            
        self.max_context_length = self.nlp_config.get("max_context_length", 500)
        
        # Initialize NLP model
        self.nlp_model = None
        if self.model_type == "spacy" and SPACY_AVAILABLE:
            try:
                self.nlp_model = spacy.load("en_core_web_md")
                logger.info("Loaded spaCy model for content analysis")
            except OSError:
                logger.warning("spaCy model not found, using fallback relevance scoring")
                self.model_type = "fallback"
                    
        # Negative keywords that indicate we should not engage
        self.negative_keywords = set(
            kw.lower() for kw in self.nlp_config.get("negative_keywords", [])
        )
        
        # Create product keyword dictionaries
        self.product_keywords = self._extract_product_keywords()
        
        # Cache
        self.cache_enabled = self.nlp_config.get("cache_responses", True)
        self.cache = {}
        self._load_cache()
        
    def _extract_product_keywords(self) -> Dict[str, Set[str]]:
        """
        Extract keywords for each product from the configuration.
        
        Returns:
            Dictionary mapping product IDs to sets of keywords
        """
        product_keywords = {}
        
        for product_id, product_data in self.products_config.items():
            # Extract keywords from config
            keywords = set(kw.lower() for kw in product_data.get("keywords", []))
            
            # Add product name as a keyword
            product_name = product_data.get("name", "")
            if product_name:
                keywords.add(product_name.lower())
                
            # Add target audience as keywords
            target_audience = product_data.get("target_audience", [])
            for audience in target_audience:
                keywords.add(audience.lower())
                
            # Add primary benefits as keywords
            benefits = product_data.get("benefits", [])
            for benefit in benefits:
                # Extract key terms from benefits
                benefit_terms = benefit.lower().split()
                for term in benefit_terms:
                    if len(term) > 3:
                        keywords.add(term)
                
            # Add additional keywords based on product description
            description = product_data.get("description", "")
            if description:
                # Extract key terms from description
                if NLTK_AVAILABLE:
                    # Extract key terms from description using nltk
                    desc_terms = set(
                        term.lower() for term in description.split() 
                        if len(term) > 3 and term.lower() not in stopwords.words('english')
                    )
                else:
                    # Simple fallback if nltk not available
                    desc_terms = set(
                        term.lower() for term in description.split() 
                        if len(term) > 3 and term.lower() not in 
                        {'the', 'and', 'for', 'with', 'that', 'this', 'are', 'was', 'were'}
                    )
                keywords.update(desc_terms)
                
            product_keywords[product_id] = keywords
            
        return product_keywords
    
    def _load_cache(self) -> None:
        """Load the analysis cache from disk if it exists."""
        if not self.cache_enabled:
            return
            
        cache_dir = self.config.get("general", {}).get("cache_directory", "data/cache")
        cache_file = os.path.join(cache_dir, "content_analyzer_cache.pkl")
        
        try:
            if os.path.exists(cache_file):
                with open(cache_file, "rb") as f:
                    self.cache = pickle.load(f)
                logger.info(f"Loaded analysis cache with {len(self.cache)} entries")
        except Exception as e:
            logger.warning(f"Failed to load analysis cache: {e}")
            self.cache = {}
            
    def _save_cache(self) -> None:
        """Save the analysis cache to disk."""
        if not self.cache_enabled:
            return
            
        cache_dir = self.config.get("general", {}).get("cache_directory", "data/cache")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        cache_file = os.path.join(cache_dir, "content_analyzer_cache.pkl")
        
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(self.cache, f)
            logger.debug(f"Saved analysis cache with {len(self.cache)} entries")
        except Exception as e:
            logger.warning(f"Failed to save analysis cache: {e}")
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for analysis.
        
        Args:
            text: The text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
            
        # Limit text length
        if len(text) > self.max_context_length:
            text = text[:self.max_context_length]
            
        # Convert to lowercase
        text = text.lower()
        
        # Replace URLs with placeholders
        text = re.sub(r'https?://\S+', '[URL]', text)
        
        # Replace special characters with spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
        
    def _contains_negative_keywords(self, text: str) -> bool:
        """
        Check if the text contains negative keywords that indicate we should not engage.
        
        Args:
            text: The text to check
            
        Returns:
            True if negative keywords are found, False otherwise
        """
        text_lower = text.lower()
        
        for keyword in self.negative_keywords:
            if keyword in text_lower:
                logger.info(f"Found negative keyword: {keyword}")
                return True
                
        return False
        
    def _get_matching_products(self, text: str) -> List[str]:
        """
        Identify which products match the text based on keywords.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of product IDs that match the text
        """
        text_lower = text.lower()
        matching_products = []
        
        for product_id, keywords in self.product_keywords.items():
            # Check if any keywords match
            if any(keyword in text_lower for keyword in keywords):
                matching_products.append(product_id)
                
        return matching_products
        
    def _calculate_relevance_score_spacy(self, text: str) -> float:
        """
        Calculate relevance score using spaCy's semantic similarity.
        
        Args:
            text: The text to analyze
            
        Returns:
            Relevance score between 0 and 1
        """
        if not self.nlp_model or not SPACY_AVAILABLE:
            logger.warning("spaCy model not available, using fallback relevance scoring")
            return self._calculate_relevance_score_fallback(text)
            
        try:
            # Process the text with spaCy
            doc = self.nlp_model(text)
            
            # Calculate scores by comparing with product descriptions
            scores = []
            
            for product_id, product_data in self.products_config.items():
                description = product_data.get("description", "")
                
                if description:
                    # Process product description
                    product_doc = self.nlp_model(description)
                    
                    # Calculate similarity
                    similarity = doc.similarity(product_doc)
                    scores.append(similarity)
                    
            # Return the maximum similarity if any scores were calculated
            if scores:
                return max([min(score, 1.0) for score in scores])
                
            return 0.0
            
        except Exception as e:
            logger.warning(f"Error calculating spaCy relevance score: {e}")
            return self._calculate_relevance_score_fallback(text)
            
    def _calculate_relevance_score_fallback(self, text: str) -> float:
        """
        Calculate relevance score using a simple keyword-based approach.
        
        Args:
            text: The text to analyze
            
        Returns:
            Relevance score between 0 and 1
        """
        text_lower = text.lower()
        total_matches = 0
        total_keywords = 0
        
        for product_id, keywords in self.product_keywords.items():
            # Count the number of keyword matches
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            total_matches += matches
            total_keywords += len(keywords)
            
        # Calculate score based on proportion of matching keywords
        if total_keywords == 0:
            return 0.0
            
        raw_score = total_matches / total_keywords
        
        # Normalize to a reasonable range (0 to 1)
        return min(raw_score * 5, 1.0)
        
    def analyze_content(self, text: str, extra_keywords: List[str] = None) -> Tuple[List[str], float]:
        """
        Analyze content to determine relevance and matching products.
        
        Args:
            text: Content text to analyze
            extra_keywords: Additional keywords to consider in the analysis (e.g., niche-specific keywords)
            
        Returns:
            Tuple of (matching product IDs, relevance score)
        """
        if not text:
            return [], 0.0
            
        # Check cache first if enabled
        if self.cache_enabled:
            cache_key = f"{hash(text)}-{hash(str(extra_keywords))}"
            if cache_key in self.cache:
                return self.cache[cache_key]
                
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Check for negative keywords
        if self._contains_negative_keywords(processed_text):
            # Negative keywords found, don't engage
            return [], 0.0
            
        # Get matching products
        matching_products = self._get_matching_products(processed_text)
        
        # Add extra keywords to the text for relevance calculation if provided
        if extra_keywords:
            # Add extra keywords to the text by creating an augmented version
            # This increases the chance of matching with related content
            extra_keywords_text = " ".join(extra_keywords)
            augmented_text = f"{processed_text} {extra_keywords_text}"
            relevance_text = augmented_text
        else:
            relevance_text = processed_text
            
        # Calculate relevance score
        if self.model_type == "spacy" and self.nlp_model:
            relevance_score = self._calculate_relevance_score_spacy(relevance_text)
        else:
            relevance_score = self._calculate_relevance_score_fallback(relevance_text)
            
        # Boost relevance score for content that matches multiple products
        if len(matching_products) > 1:
            relevance_score = min(1.0, relevance_score * 1.2)
            
        # Store result in cache
        if self.cache_enabled:
            self.cache[cache_key] = (matching_products, relevance_score)
            self._save_cache()
            
        return matching_products, relevance_score 