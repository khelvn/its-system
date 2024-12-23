from owlready2 import *
from config import Config
import logging
import os

logger = logging.getLogger(__name__)

class OntologyManager:
    def __init__(self):
        self.onto_path = Config.ONTOLOGY_PATH
        self.onto = self.load_ontology()
        
    def load_ontology(self):
        """Load the geometry ontology"""
        try:
            full_path = os.path.abspath(self.onto_path)
            logger.debug(f"Loading ontology from: {full_path}")
            
            if not os.path.exists(full_path):
                logger.error(f"Ontology file not found at: {full_path}")
                raise FileNotFoundError(f"Ontology file not found at: {full_path}")
            
            onto_path.append(os.path.dirname(full_path))
            logger.debug("Starting to load ontology...")
            onto = get_ontology(f"file://{full_path}").load()
            
            # Debug information
            logger.debug(f"Successfully loaded ontology with {len(list(onto.classes()))} classes")
            logger.debug("Available Classes:")
            for cls in onto.classes():
                logger.debug(f"- {cls.name}")
            
            logger.debug("Available Properties:")
            for prop in onto.properties():
                logger.debug(f"- {prop.name}")
                
            return onto
        except Exception as e:
            logger.error(f"Error loading ontology: {e}")
            raise

    def get_problems_by_difficulty(self, difficulty, shape_type):
        """Get problems of specific difficulty for a specific shape"""
        try:
            problems = []
            shape_name = shape_type.capitalize()
            logger.debug(f"Looking for {shape_name} problems with difficulty: {difficulty}")

            # Get all instances of Problem class
            for problem in self.onto.Problem.instances():
                try:
                    # Only consider problems that match the shape name
                    if not problem.name.startswith(f"{shape_name}_"):
                        continue
                        
                    logger.debug(f"Examining problem: {problem}")
                    problem_difficulty = None
                    
                    # Use the correct property name with parentheses
                    if hasattr(problem, "hasDifficultyLevel_(string)"):
                        difficulty_values = getattr(problem, "hasDifficultyLevel_(string)")
                        if difficulty_values:
                            problem_difficulty = difficulty_values[0]
                            if problem_difficulty == difficulty:
                                logger.debug(f"Found matching problem: {problem}")
                                problems.append(problem)
                
                except Exception as e:
                    logger.error(f"Error processing problem {problem}: {str(e)}")
                    continue
            
            logger.debug(f"Found {len(problems)} {shape_name} problems with difficulty {difficulty}")
            return problems
        except Exception as e:
            logger.error(f"Error getting problems for difficulty {difficulty}: {str(e)}")
            return []

    def get_shape_by_name(self, shape_name):
        """Get specific shape by name"""
        try:
            # First try direct lookup
            for shape_class in self.onto.TwoDimensionalShape.descendants():
                logger.debug(f"Checking shape class: {shape_class.name}")
                if shape_class.name.lower() == shape_name.lower():
                    # Get or create an instance
                    instances = list(shape_class.instances())
                    if instances:
                        return instances[0]
                    else:
                        new_instance = shape_class()
                        return new_instance
            
            # Try looking through all geometric shapes if not found in 2D shapes
            for shape_class in self.onto.GeometricShape.descendants():
                logger.debug(f"Checking geometric shape: {shape_class.name}")
                if shape_class.name.lower() == shape_name.lower():
                    instances = list(shape_class.instances())
                    if instances:
                        return instances[0]
                    else:
                        new_instance = shape_class()
                        return new_instance
            
            logger.warning(f"Shape not found: {shape_name}")
            return None
        except Exception as e:
            logger.error(f"Error getting shape {shape_name}: {e}")
            return None

    def get_learning_path(self, shape_type):
        """Generate learning path for a shape type"""
        try:
            logger.debug(f"Getting learning path for: {shape_type}")
            shape = self.get_shape_by_name(shape_type)
            if not shape:
                logger.warning(f"Shape not found: {shape_type}")
                return self._empty_learning_path()

            logger.debug(f"Found shape: {shape}")
            result = {
                'definitions': [],
                'formulas': [],
                'examples': [],
                'problems': []
            }

            # Get shape-specific definitions
            shape_name = shape_type.capitalize()
            logger.debug(f"Looking for content with prefix: {shape_name}_")
            
            # Get definitions
            for def_inst in self.onto.Definition.instances():
                if def_inst.name.startswith(f"{shape_name}_"):
                    logger.debug(f"Found matching definition: {def_inst.name}")
                    if hasattr(def_inst, "hasDescription_(string)"):
                        desc = getattr(def_inst, "hasDescription_(string)")
                        if desc:
                            result['definitions'].append({'description': desc[0]})

            # Get formulas
            for formula in self.onto.Formula.instances():
                if formula.name.startswith(f"{shape_name}_"):
                    logger.debug(f"Found matching formula: {formula.name}")
                    formula_data = {'formula': '', 'description': ''}
                    if hasattr(formula, "hasFormula_(string)"):
                        formula_values = getattr(formula, "hasFormula_(string)")
                        if formula_values:
                            formula_data['formula'] = formula_values[0]
                    if hasattr(formula, "hasDescription_(string)"):
                        desc_values = getattr(formula, "hasDescription_(string)")
                        if desc_values:
                            formula_data['description'] = desc_values[0]
                    if formula_data['formula'] or formula_data['description']:
                        result['formulas'].append(formula_data)

            # Get examples
            for example in self.onto.Example.instances():
                if example.name.startswith(f"{shape_name}_"):
                    logger.debug(f"Found matching example: {example.name}")
                    example_data = {'description': '', 'steps': []}
                    if hasattr(example, "hasDescription_(string)"):
                        desc_values = getattr(example, "hasDescription_(string)")
                        if desc_values:
                            example_data['description'] = desc_values[0]
                    if hasattr(example, "hasStep_(string)"):
                        step_values = getattr(example, "hasStep_(string)")
                        if step_values:
                            example_data['steps'] = list(step_values)
                    if example_data['description'] or example_data['steps']:
                        result['examples'].append(example_data)

            # Get problems
            for problem in self.onto.Problem.instances():
                if problem.name.startswith(f"{shape_name}_"):
                    logger.debug(f"Found matching problem: {problem.name}")
                    problem_data = self._get_problem_data(problem)
                    if problem_data:
                        result['problems'].append(problem_data)

            logger.debug(f"Final learning path for {shape_type}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting learning path for {shape_type}: {e}")
            return self._empty_learning_path()

    def _get_problem_data(self, problem):
        """Extract problem data"""
        try:
            data = {
                'description': '',
                'difficulty': 'easy',
                'steps': [],
                'answer': 0.0,
                'unit': ''
            }
            
            #  property names with parentheses
            if hasattr(problem, "hasDescription_(string)"):
                values = getattr(problem, "hasDescription_(string)")
                if values:
                    data['description'] = values[0]
            
            if hasattr(problem, "hasDifficultyLevel_(string)"):
                values = getattr(problem, "hasDifficultyLevel_(string)")
                if values:
                    data['difficulty'] = values[0]
            
            if hasattr(problem, "hasStep_(string)"):
                values = getattr(problem, "hasStep_(string)")
                if values:
                    data['steps'] = list(values)
            
            if hasattr(problem, "correctAnswer_(decimal)"):
                values = getattr(problem, "correctAnswer_(decimal)")
                if values:
                    try:
                        data['answer'] = float(values[0])
                    except (ValueError, TypeError):
                        pass
            
            if hasattr(problem, "hasUnit_(string)"):
                values = getattr(problem, "hasUnit_(string)")
                if values:
                    data['unit'] = values[0]
            
            logger.debug(f"Extracted problem data: {data}")
            return data
        except Exception as e:
            logger.error(f"Error extracting problem data: {str(e)}")
            return None

    def _empty_learning_path(self):
        """Return empty learning path structure"""
        return {
            'definitions': [],
            'formulas': [],
            'examples': [],
            'problems': []
        }