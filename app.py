from flask import Flask, render_template, request, jsonify, session
from models.ontology import OntologyManager
from models.bkt import BKTModel
from config import Config
import logging
import os 

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Initialize managers
ontology = OntologyManager()
bkt_models = {}

@app.route('/')
def index():
    """Render the dashboard with available geometry topics"""
    return render_template('dashboard.html', topics=Config.GEOMETRY_TOPICS)

@app.route('/get_problem/<topic>/<difficulty>')
def get_problem(topic, difficulty):
    """Get a problem of specified difficulty for the topic"""
    try:
        problems = ontology.get_problems_by_difficulty(difficulty, topic)
        if not problems:
            logger.warning(f"No problems found for {topic} with difficulty {difficulty}")
            return jsonify({
                'description': 'No more problems available at this difficulty level.',
                'steps': [],
                'answer': 0,
                'unit': 'units'
            })
        
        # fetch first available problem
        problem = problems[0]
        logger.debug(f"Found problem: {problem}")
        
        # Extract problem data using _get_problem_data method
        problem_data = ontology._get_problem_data(problem)
        if not problem_data:
            logger.error("Failed to extract problem data")
            return jsonify({
                'description': 'Problem is currently unavailable. Please try again.',
                'steps': [],
                'answer': 0,
                'unit': 'units'
            })
        
        logger.debug(f"Problem data: {problem_data}")
        return jsonify(problem_data)
    except Exception as e:
        logger.error(f"Error getting problem: {str(e)}")
        return jsonify({
            'description': 'Error loading problem. Please try again.',
            'steps': [],
            'answer': 0,
            'unit': 'units'
        })

@app.route('/topic/<topic_name>')
def topic_page(topic_name):
    if topic_name not in session:
        session[topic_name] = {
            'current_level': 'easy',
            'problems_solved': 0,
            'correct_answers': 0
        }
    
    learning_path = ontology.get_learning_path(topic_name)
    logger.debug(f"Learning path for {topic_name}: {learning_path}")
    
    return render_template('problem.html',
                         topic=topic_name,
                         learning_path=learning_path,
                         progress=session[topic_name])

@app.route('/check_answer', methods=['POST'])
def check_answer():
    """Check student's answer and update learning model"""
    try:
        data = request.get_json()
        logger.debug(f"Received answer data: {data}")
        
        topic = data.get('topic')
        student_answer = float(data.get('answer', 0))
        student_unit = data.get('unit', '')
        correct_answer = float(data.get('correct_answer', 0))
        expected_unit = data.get('expected_unit', '')
        
        if not all([topic, student_answer, student_unit, correct_answer, expected_unit]):
            return jsonify({
                'error': 'Missing required data',
                'correct': False
            }), 400
        
        # Initialize BKT model for topic
        if topic not in bkt_models:
            bkt_models[topic] = BKTModel()
        
        # Check if answer is correct
        is_answer_correct = abs(student_answer - correct_answer) < 0.01
        is_unit_correct = student_unit.lower() == expected_unit.lower()
        is_correct = is_answer_correct and is_unit_correct
        
        # Update BKT model
        bkt_models[topic].update_knowledge(is_correct)
        
        # Update session progress
        if topic in session:
            session[topic]['problems_solved'] += 1
            if is_correct:
                session[topic]['correct_answers'] += 1
            session[topic]['current_level'] = bkt_models[topic].get_next_problem_difficulty()
            session.modified = True
        
        return jsonify({
            'correct': is_correct,
            'next_difficulty': session[topic]['current_level'],
            'progress': session[topic]
        })
    except Exception as e:
        logger.error(f"Error checking answer: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reset')
def reset_all():
    """Reset all data - clear session and database"""
    try:
        # Clear session
        session.clear()
        
        # Reset all BKT models
        global bkt_models
        bkt_models = {}
        
        # SQLite, we can remove the database file
        db_path = 'geometry_tutor.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            
        return render_template('dashboard.html', topics=Config.GEOMETRY_TOPICS)
    except Exception as e:
        return jsonify({'error': f'Error resetting data: {str(e)}'}), 500
    
if __name__ == '__main__':
    app.run(debug=True)