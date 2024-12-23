import os
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Config:
    # Basic Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_123')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///geometry_tutor.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application Config
    _base_dir = os.path.dirname(os.path.abspath(__file__))
    ONTOLOGY_PATH = os.path.join(_base_dir, 'knowledge', 'geometry.owl')
    
    # Log the path for debugging
    logger.debug(f"Base directory: {_base_dir}")
    logger.debug(f"Full ontology path: {ONTOLOGY_PATH}")
    
    # Verify the file exists
    if not os.path.exists(ONTOLOGY_PATH):
        logger.error(f"Ontology file not found at: {ONTOLOGY_PATH}")
    else:
        logger.debug(f"Ontology file exists at: {ONTOLOGY_PATH}")
    
    # BKT Model Parameters
    BKT_PARAMS = {
        'init_p_know': 0.5,  # Initial probability of knowledge
        'learn_rate': 0.1,   # Learning rate
        'forget_rate': 0.1,  # Forgetting rate
        'guess_rate': 0.2,   # Guess probability
        'slip_rate': 0.1     # Slip probability
    }
    
    # Geometry Topics
    GEOMETRY_TOPICS = [
        'triangle',
        'square',
        'rectangle',
        'circle',
        'cube',
        'sphere'
    ]
    
    # Difficulty Levels
    DIFFICULTY_LEVELS = ['easy', 'medium', 'hard']