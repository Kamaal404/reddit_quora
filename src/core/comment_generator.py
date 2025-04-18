"""
Comment Generator for creating relevant and personalized comments.
"""

import logging
import os
import random
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.config.persona import PERSONA
from src.config.products import PRODUCTS
from src.config.templates import (
    PRODUCT_TEMPLATES, GENERAL_TEMPLATES, TIME_PERIODS, SPECIFIC_BENEFITS, 
    PERSONAL_ISSUES, MECHANISMS, SPECIFIC_FREQUENCIES, SPIRITUAL_PRACTICES,
    TECHNOLOGIES, RELATED_PRODUCTS, PERSONAL_STORIES, TRADITIONAL_PRINCIPLES,
    GENERAL_BENEFITS
)

logger = logging.getLogger(__name__)


class CommentGenerator:
    """
    Generates contextually appropriate comments for social media platforms.
    
    Uses templates and personalization techniques to create comments
    that sound natural and promote QiLifeStore products subtly.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the CommentGenerator.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.products_config = PRODUCTS
        self.comment_config = config.get("comment_generation", {})
        
        # Use persona from dedicated module
        self.persona_config = PERSONA
        
        # Load templates from dedicated module
        self.product_templates = PRODUCT_TEMPLATES
        self.general_templates = GENERAL_TEMPLATES
        
        # Niche-specific configuration
        self.niches_enabled = config.get("general", {}).get("niches_enabled", False)
        self.tailor_by_niche = self.comment_config.get("tailor_comments_by_niche", False)
        
        # Load templates
        self.templates = self._load_templates()
        
        # Create persona-related elements from PERSONA
        self.personal_experiences = self._create_personal_experiences()
            
        # Product transition phrases to naturally introduce products
        self.transition_phrases = [
            "You might want to look into {product}. {reason}",
            "Based on my experience, {product} could be worth considering. {reason}",
            "Have you explored {product} yet? {reason}",
            "Something that worked well for me was {product}. {reason}",
            "Many people in the biohacking community have had success with {product}. {reason}",
            "For concerns like yours, {product} might be helpful. {reason}",
            "I've had positive results with {product} for similar issues. {reason}",
            "An option worth researching is {product}. {reason}"
        ]
        
        # Introduction phrases for starting comments
        self.intro_phrases = [
            "Great question! ",
            "I've been exploring this area for a while. ",
            "This is something I've researched extensively. ",
            "As someone who's been in your position, ",
            "I understand what you're looking for. ",
            "I've had similar questions on my wellness journey. ",
            "This is actually a topic I'm passionate about. ",
            "From my experience in the biohacking community, "
        ]
        
        # Closing phrases for ending comments
        self.closing_phrases = [
            "Hope that helps!",
            "Wishing you the best on your wellness journey.",
            "Let me know if you have any other questions.",
            "Hope you find something that works for you.",
            "Would love to hear how it goes if you try it.",
            "Everyone's experience is different, but this is what worked for me.",
            "Just sharing my personal experience - your results may vary.",
            "Hope this gives you some useful direction."
        ]
        
        logger.info(f"Initialized CommentGenerator with {len(self.product_templates)} product templates and {len(self.general_templates)} general templates")
    
    def _create_personal_experiences(self) -> Dict[str, List[str]]:
        """
        Create personal experience snippets based on persona configuration.
        
        Returns:
            Dictionary mapping product IDs to lists of personal experience snippets
        """
        # Personal experience snippets for the David Wong persona
        experiences = {
            "qi_coil": [
                "I've been using the Qi Coil for about a year now, and it's been a game-changer for my sleep quality.",
                "When I first tried the Qi Coil, I was skeptical, but after consistent use, I noticed significant improvements in my energy levels.",
                "As someone who struggled with chronic tension, the Qi Coil has become an essential part of my evening routine.",
                "I keep my Qi Coil right on my desk and use it throughout my workday for quick mental refreshes."
            ],
            "qi_coil_aura": [
                "The Qi Coil Aura has become my go-to device for deeper meditative states - the expanded frequency range really makes a difference.",
                "After upgrading to the Qi Coil Aura, I noticed more pronounced effects, especially when working with the higher frequencies.",
                "The Qi Coil Aura's versatility has allowed me to address several wellness goals simultaneously.",
                "What I love about the Qi Coil Aura is how I can target specific areas with precision."
            ],
            "quantum_frequencies": [
                "The Quantum Frequencies packages have allowed me to customize my PEMF sessions based on exactly what my body needs that day.",
                "I travel frequently and the Quantum Frequencies digital packages are perfect - no extra equipment needed beyond my Qi Coil.",
                "The sleep frequency package has been particularly effective for me during periods of stress.",
                "I've built a personalized library of Quantum Frequencies that I rotate through depending on what I'm trying to accomplish."
            ],
            "qi_resonance_sound_bed": [
                "The full-body immersion of the Qi Resonance Sound Bed creates an experience that's hard to describe but incredibly restorative.",
                "When I invested in the Qi Resonance Sound Bed, it completely transformed my approach to deep relaxation.",
                "The difference between targeted PEMF and the full-body experience of the Qi Resonance Sound Bed is quite remarkable.",
                "I've set up a dedicated space for my Qi Resonance Sound Bed - it's become my daily reset button."
            ],
            "qi_red_light_therapy": [
                "Adding the Qi Red Light Therapy to my morning routine has noticeably improved my skin and overall energy levels.",
                "I use the Qi Red Light Therapy after workouts, and it seems to help with recovery time significantly.",
                "The combination of near-infrared and red light from the Qi device feels more comprehensive than other products I've tried.",
                "The portability of the Qi Red Light Therapy panel means I can use it while working or reading."
            ],
            "qi_wand": [
                "The precision of the Qi Wand has been perfect for addressing specific acupressure points and small areas of tension.",
                "I keep the Qi Wand in my bag so I can use it whenever I feel tension building up during the day.",
                "The combination of cold laser and acupressure in the Qi Wand has been particularly effective for headache relief for me.",
                "For targeted therapy, the Qi Wand has become my first choice - it's simple but remarkably effective."
            ]
        }
        
        return experiences
    
    def _load_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Load comment templates from files and from the templates module.
        
        Returns:
            Dictionary mapping platform and product to lists of templates
        """
        # Initialize empty templates structure
        templates = {
            "reddit": {},
            "quora": {}
        }
        
        # First, load the predefined product templates for both platforms
        for platform in templates.keys():
            for product_id, product_template_list in self.product_templates.items():
                templates[platform][product_id] = product_template_list.copy()
            
            # Add general templates to each platform
            templates[platform]["general"] = self.general_templates.copy()
        
        # Then try to load any custom templates from the filesystem
        templates_dir = self.comment_config.get("templates_directory", "src/templates")
        
        try:
            # Check if templates directory exists
            if not os.path.exists(templates_dir):
                logger.warning(f"Templates directory not found: {templates_dir}")
                # Create the directory structure
                os.makedirs(os.path.join(templates_dir, "reddit"), exist_ok=True)
                os.makedirs(os.path.join(templates_dir, "quora"), exist_ok=True)
                logger.info(f"Created templates directories for Reddit and Quora")
                
            # Create platform directories if they don't exist
            for platform in templates.keys():
                platform_dir = os.path.join(templates_dir, platform)
                if not os.path.exists(platform_dir):
                    os.makedirs(platform_dir, exist_ok=True)
                    logger.info(f"Created templates directory for {platform}")
                    
            # Load platform-specific templates from filesystem
            for platform in templates.keys():
                platform_dir = os.path.join(templates_dir, platform)
                
                # Check for general templates file
                general_template_file = os.path.join(platform_dir, "general.txt")
                if os.path.exists(general_template_file):
                    with open(general_template_file, "r") as f:
                        file_templates = [
                            line.strip() for line in f.readlines()
                            if line.strip() and not line.strip().startswith("#")
                        ]
                        # Add these templates to any existing ones
                        templates[platform]["general"].extend(file_templates)
                        logger.info(f"Loaded {len(file_templates)} additional general templates on {platform}")
                
                # Load product-specific templates
                for product_id in self.products_config.keys():
                    template_file = os.path.join(platform_dir, f"{product_id}.txt")
                    
                    if os.path.exists(template_file):
                        with open(template_file, "r") as f:
                            file_templates = [
                                line.strip() for line in f.readlines()
                                if line.strip() and not line.strip().startswith("#")
                            ]
                            # Add these templates to any existing ones
                            if product_id in templates[platform]:
                                templates[platform][product_id].extend(file_templates)
                            else:
                                templates[platform][product_id] = file_templates
                            
                            logger.info(f"Loaded {len(file_templates)} additional templates for {product_id} on {platform}")
                    
                    # Load niche-specific templates if niches are enabled
                    if self.niches_enabled and self.tailor_by_niche:
                        try:
                            from src.config.niches import NICHES
                            for niche in NICHES:
                                niche_template_file = os.path.join(
                                    platform_dir, 
                                    f"{product_id}_{niche}.txt"
                                )
                                
                                if os.path.exists(niche_template_file):
                                    with open(niche_template_file, "r") as f:
                                        niche_templates = [
                                            line.strip() for line in f.readlines()
                                            if line.strip() and not line.strip().startswith("#")
                                        ]
                                        templates[platform][f"{product_id}_{niche}"] = niche_templates
                                        logger.info(
                                            f"Loaded {len(niche_templates)} "
                                            f"niche-specific templates for {product_id} and {niche} on {platform}"
                                        )
                        except ImportError:
                            logger.warning("Could not import niches configuration for template loading")
            
            logger.info(f"Completed loading templates for {len(templates['reddit'])} categories on Reddit and {len(templates['quora'])} on Quora")
            return templates
            
        except Exception as e:
            logger.exception(f"Error loading templates: {e}")
            return self._get_default_templates()
    
    def _get_default_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get default templates from the product templates module.
        
        Returns:
            Dictionary mapping platform and product to lists of templates
        """
        # Use the predefined product templates for both platforms
        templates = {
            "reddit": {},
            "quora": {}
        }
        
        for platform in templates.keys():
            for product_id, product_template_list in self.product_templates.items():
                templates[platform][product_id] = product_template_list.copy()
            
            # Add general templates
            templates[platform]["general"] = self.general_templates.copy()
        
        logger.info("Using default product and general templates from templates module")
        return templates
    
    def _format_template(self, template: str, substitutions: Dict[str, str]) -> str:
        """
        Format a template by replacing placeholders with actual values.
        
        Args:
            template: Template string with placeholders
            substitutions: Dictionary mapping placeholders to their values
            
        Returns:
            Formatted template string
        """
        return template.format(**substitutions)
    
    def _add_persona_signature(self, comment: str) -> str:
        """
        Add the David Wong persona signature to the comment.
        
        Args:
            comment: The generated comment
            
        Returns:
            Comment with signature added
        """
        # Get persona information
        name = self.persona_config.get("name", "David Wong")
        role = self.persona_config.get("role", "Wellness Technology Expert")
        
        # Don't add signature if it's already present
        if name in comment:
            return comment
            
        # Add signature with a 30% probability
        if random.random() < 0.3:
            signature = f"\n\n- {name}, {role}"
            return comment + signature
            
        return comment
    
    def _add_product_link(self, comment: str, product_info: Dict[str, Any]) -> str:
        """
        Add product link to the comment if appropriate.
        
        Args:
            comment: The generated comment
            product_info: Dictionary containing product information
            
        Returns:
            Comment with product link added
        """
        # Check if we should include a link based on probability
        include_link_probability = self.comment_config.get("include_product_link_probability", 0.5)
        
        if random.random() > include_link_probability:
            return comment
            
        # Get product information
        product_name = product_info.get("name", "")
        product_url = product_info.get("url", "")
        
        if not product_url:
            return comment
            
        # Check if product name already appears in the comment
        if product_name in comment:
            # Replace one instance of the product name with a linked version
            product_regex = re.escape(product_name)
            pattern = fr"(?<!\[)({product_regex})(?!\])"
            
            # Only replace the first occurrence that's not already linked
            match = re.search(pattern, comment)
            if match:
                start, end = match.span(1)
                link_text = f"[{product_name}]({product_url})"
                comment = comment[:start] + link_text + comment[end:]
                
        else:
            # Product name not in comment, add a subtle mention with link
            product_mention = f"\n\nIf you want to learn more, you can check out [{product_name}]({product_url})."
            comment += product_mention
            
        return comment
    
    def generate_comment(self, platform: str, content_text: str, product_matches: List[str], relevance_score: float = 0.0, niche: Optional[str] = None) -> Optional[str]:
        """
        Generate a comment based on the content and matched products.
        
        Args:
            platform: The platform to generate the comment for (e.g., "reddit", "quora")
            content_text: The text of the post/question to respond to
            product_matches: List of product IDs that match the content
            relevance_score: The relevance score of the content (0.0-1.0)
            niche: The niche category for tailoring the comment (optional)
            
        Returns:
            Generated comment text, or None if generation failed
        """
        if not product_matches:
            logger.warning("No product matches provided, cannot generate comment")
            return None
            
        try:
            # Select a product to focus on (prioritize higher relevance score)
            main_product = random.choice(product_matches)
            product_info = self.products_config.get(main_product, {})
            
            # Get suitable templates for this platform
            platform_templates = self.templates.get(platform, {})
            
            # Decide whether to use a general template (20% chance) or product-specific template
            use_general_template = random.random() < 0.2
            
            if use_general_template:
                # Get general templates
                general_templates = platform_templates.get("general", [])
                if general_templates:
                    template = random.choice(general_templates)
                    logger.info(f"Using general template for {main_product}")
                else:
                    # Fall back to product-specific template if no general templates
                    use_general_template = False
            
            if not use_general_template:
                # Get templates for this specific product
                product_templates = platform_templates.get(main_product, [])
                
                # If we have niche-specific templates and niche is provided, try to use those
                niche_template = None
                if self.niches_enabled and self.tailor_by_niche and niche:
                    # Look for niche-specific templates
                    niche_templates = platform_templates.get(f"{main_product}_{niche}", [])
                    if niche_templates:
                        niche_template = random.choice(niche_templates)
                        logger.info(f"Using niche-specific template for {niche}")
                
                # If no templates found for this product, use generic templates
                if not product_templates and not niche_template:
                    product_templates = platform_templates.get("general", [])
                    
                # If still no templates, return a simple generic response
                if not product_templates and not niche_template:
                    logger.warning(f"No templates found for {platform} and {main_product}")
                    return self._generate_fallback_comment(product_info)
                    
                # Select a template
                template = niche_template if niche_template else random.choice(product_templates)
            
            # Prepare for template substitution
            substitutions = self._prepare_template_substitutions(main_product, product_info, niche, use_general_template)
            
            # Format the template
            comment = self._format_template(template, substitutions)
            
            # Add personalization
            comment = self._add_personalization(comment)
            
            # Add product link if configured
            if random.random() < self.comment_config.get("include_product_link_probability", 0.5):
                comment = self._add_product_link(comment, product_info)
                
            # Add persona signature
            comment = self._add_persona_signature(comment)
                
            return comment
            
        except Exception as e:
            logger.exception(f"Error generating comment: {e}")
            return None
    
    def _prepare_template_substitutions(self, product_id: str, product_info: Dict[str, Any], niche: Optional[str] = None, is_general_template: bool = False) -> Dict[str, str]:
        """
        Prepare substitution values for template placeholders.
        
        Args:
            product_id: ID of the product being recommended
            product_info: Information about the product
            niche: Niche category if available
            is_general_template: Whether using a general template instead of product-specific
            
        Returns:
            Dictionary of substitution values
        """
        # Start with common substitutions
        substitutions = {
            "product_name": product_info.get("name", "our product"),
            "PRODUCT_NAME": product_info.get("name", "our product"),
            "product_description": product_info.get("description", ""),
            "PRODUCT_DESC": product_info.get("description", ""),
            "PRODUCT_URL": product_info.get("url", "https://qilifestore.com"),
            "PERSONA_NAME": self.persona_config.get("name", "David"),
            "CURRENT_YEAR": str(datetime.now().year)
        }
        
        # Add a personal experience snippet
        personal_experiences = self.personal_experiences.get(product_id, [])
        if personal_experiences:
            substitutions["personal_experience"] = random.choice(personal_experiences)
        else:
            substitutions["personal_experience"] = ""
            
        # Add time period
        substitutions["time_period"] = random.choice(TIME_PERIODS)
        
        # Add niche target for the template
        target_niche = niche or "general"
        
        # Add specific benefits based on niche if available
        if target_niche in SPECIFIC_BENEFITS:
            specific_benefits = SPECIFIC_BENEFITS[target_niche]
            substitutions["specific_benefit"] = random.choice(specific_benefits)
        else:
            # Fallback to a generic benefit
            generic_benefits = [
                "improved wellness", "enhanced relaxation", "better energy levels",
                "overall improvement", "noticeable results"
            ]
            substitutions["specific_benefit"] = random.choice(generic_benefits)
            
        # Add personal issue based on niche if available
        if target_niche in PERSONAL_ISSUES:
            personal_issues = PERSONAL_ISSUES[target_niche]
            substitutions["personal_issue"] = random.choice(personal_issues)
        else:
            # Fallback to generic issues
            generic_issues = [
                "health concerns", "wellness challenges", "stress-related issues",
                "daily challenges", "persistent concerns"
            ]
            substitutions["personal_issue"] = random.choice(generic_issues)
            
        # Add mechanism
        substitutions["mechanism"] = random.choice(MECHANISMS)
        
        # Add specific frequency
        substitutions["specific_frequency"] = random.choice(SPECIFIC_FREQUENCIES)
        
        # Add spiritual practice
        substitutions["spiritual_practice"] = random.choice(SPIRITUAL_PRACTICES)
        
        # If using a general template, add additional substitutions
        if is_general_template:
            # Add technology based on niche if available
            if target_niche in TECHNOLOGIES:
                technologies = TECHNOLOGIES[target_niche]
                substitutions["technology"] = random.choice(technologies)
            else:
                # Fallback to generic technology
                generic_technologies = ["wellness technology", "frequency-based approaches", "energy medicine"]
                substitutions["technology"] = random.choice(generic_technologies)
                
            # Add related product options
            if product_id in RELATED_PRODUCTS:
                related_products = RELATED_PRODUCTS[product_id]
                substitutions["related_product"] = random.choice(related_products)
            else:
                substitutions["related_product"] = product_info.get("name", "our wellness technology")
                
            # Add personal story
            substitutions["personal_story"] = random.choice(PERSONAL_STORIES)
            
            # Add traditional principle
            substitutions["traditional_principle"] = random.choice(TRADITIONAL_PRINCIPLES)
            
            # Add benefit (general)
            substitutions["benefit"] = random.choice(GENERAL_BENEFITS)
        
        # Add niche-specific terms if applicable
        if niche:
            substitutions["NICHE"] = niche.replace("_", " ").title()
            
        return substitutions
    
    def _generate_fallback_comment(self, product_info: Dict[str, Any]) -> str:
        """
        Generate a fallback comment when no suitable templates are found.
        
        Args:
            product_info: Dictionary containing product information
            
        Returns:
            Generated fallback comment
        """
        # Get product name and description
        product_name = product_info.get("name", "our product")
        product_description = product_info.get("description", "wellness technology")
        
        # Create a simple generic response
        fallback_templates = [
            f"I've been exploring {product_description} and found {product_name} to be quite effective for my needs.",
            f"From my experience with {product_description}, I've had good results with {product_name}.",
            f"I've been using {product_name} for a while now, and it's been helpful as part of my wellness routine.",
            f"Many people in the wellness community have been discussing {product_name} lately. It's worth looking into if you're interested in {product_description}.",
            f"As someone who has experimented with various wellness technologies, I've found {product_name} to be particularly interesting."
        ]
        
        return random.choice(fallback_templates)
    
    def _add_personalization(self, comment: str) -> str:
        """
        Add personalized elements to the comment.
        
        Args:
            comment: The base comment
            
        Returns:
            Personalized comment with additions
        """
        # Add random intro phrase with 60% probability
        if random.random() < 0.6 and not any(phrase in comment for phrase in self.intro_phrases):
            intro = random.choice(self.intro_phrases)
            # Only add intro if it doesn't make the comment awkward
            if not comment.startswith("I ") and not comment.startswith("My "):
                comment = intro + comment
                
        # Add random closing with 40% probability
        if random.random() < 0.4 and not any(phrase in comment for phrase in self.closing_phrases):
            closing = random.choice(self.closing_phrases)
            if not comment.endswith("."):
                comment += "."
            comment += f" {closing}"
            
        return comment 