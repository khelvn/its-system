from config import Config
import numpy as np

class BKTModel:
    def __init__(self):
        params = Config.BKT_PARAMS
        self.p_know = params['init_p_know']  # P(L₀)
        self.p_learn = params['learn_rate']  # P(T)
        self.p_forget = params['forget_rate']  # P(F)
        self.p_guess = params['guess_rate']  # P(G)
        self.p_slip = params['slip_rate']  # P(S)
        
    def update_knowledge(self, correct):
        """Update knowledge state based on student response"""
        # Step 1: Calculate probability of correct response
        p_correct = (self.p_know * (1 - self.p_slip) + 
                    (1 - self.p_know) * self.p_guess)
        
        # Step 2: Update knowledge based on response
        if correct:
            self.p_know = (self.p_know * (1 - self.p_slip)) / p_correct
        else:
            self.p_know = (self.p_know * self.p_slip) / (1 - p_correct)
            
        # Step 3: Account for learning/forgetting
        self.p_know = (self.p_know * (1 - self.p_forget) + 
                      (1 - self.p_know) * self.p_learn)
        
        return self.p_know
    
    def get_next_problem_difficulty(self):
        """Determine appropriate difficulty for next problem"""
        if self.p_know < 0.3:
            return 'easy'
        elif self.p_know < 0.7:
            return 'medium'
        else:
            return 'hard'
    
    def predict_success_probability(self):
        """Predict probability of successful response"""
        return (self.p_know * (1 - self.p_slip) + 
                (1 - self.p_know) * self.p_guess)
    
    def reset(self):
        """Reset model to initial state"""
        self.__init__()