import numpy as np
import pandas as pd
import yaml
import math
import copy
import os

class MCTSNode:
    def __init__(self, state, possible_actions, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.possible_actions = possible_actions # List of action dicts
        self.untried_actions = possible_actions.copy() if possible_actions else []

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def is_terminal(self, horizon=5):
        depth = 0
        curr = self
        while curr.parent:
            depth += 1
            curr = curr.parent
        return depth >= horizon

    def best_child(self, c_param=1.4):
        # UCB Calculation
        # Normalize/Scale values? Assuming value is roughly large negative.
        # UCB = v_i/n_i + C * sqrt(ln N / n_i)
        # If values are -100, -90... -90 is better.
        # Since logic handles score = -cost.
        if not self.children:
             # Should not happen if check is done before calling best_child
             return None 
             
        choices_weights = [
            (child.value / (child.visits + 1e-6)) + c_param * np.sqrt((2 * np.log(self.visits + 1)) / (child.visits + 1e-6))
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]
        
    def expand(self, controller):
        action = self.untried_actions.pop()
        next_state = controller.step_dmc(self.state, action)
        # Pass same set of possible actions to child for recursion
        child_node = MCTSNode(next_state, self.possible_actions, parent=self, action=action)
        self.children.append(child_node)
        return child_node



class PPLController:
    def __init__(self, run_dirs=None, lime_df=None, config=None):
        """
        Initialize controller with either run directories OR direct data/config.
        Args:
           run_dirs (str or list): Single path or list of paths to run directories.
           lime_df (pd.DataFrame): Knowledge base dataframe.
           config (dict): Configuration dictionary.
        """
        if run_dirs:
            if isinstance(run_dirs, str):
                self.run_dirs = [run_dirs]
            else:
                self.run_dirs = run_dirs
                
            self.config = self._load_config()
            self.lime_df = self._load_lime_context()
        elif lime_df is not None and config is not None:
            self.run_dirs = []
            self.config = config
            self.lime_df = lime_df
        else:
            raise ValueError("Must provide either run_dirs OR (lime_df and config)")
        
        # Configuration (set by user)
        self.mvs = {} 
        self.dvs = {} 
        self.cvs = {} 
        self.objective_formula = ""
        self.objective_goal = "" 
        self.objective_weight = 10.0 # Default High Priority 
        
        # Cache for input columns to avoid repeated lookup
        self.input_cols = self.config['input_columns']
        self.output_cols = self.config['output_columns']

    def _load_config(self):
        # Load config from the first run (assuming consistent schema)
        # In a real app, verify compatibility.
        first_dir = self.run_dirs[0]
        with open(f"{first_dir}/config.yaml", 'r') as f:
            return yaml.safe_load(f)

    def _load_lime_context(self):
        dfs = []
        for d in self.run_dirs:
            path = f"{d}/lime_context_data.csv"
            if os.path.exists(path):
                dfs.append(pd.read_csv(path))
            else:
                print(f"Warning: No LIME context found in {d}")
        
        if not dfs:
            raise ValueError("No LIME context data found in any provided run directories.")
            
        return pd.concat(dfs, ignore_index=True)

    def get_gains(self, current_state):
        """
        Compute local Gain Matrix K using KNN on LIME context data.
        Returns DataFrame index=MV, columns=CV
        """
        k = 5 # Number of neighbors
        gains = pd.DataFrame(0.0, index=self.input_cols, columns=self.output_cols)
        
        # Helper: Extract input vector from state
        # State keys match input_cols?
        try:
            state_vec = np.array([current_state.get(c, 0.0) for c in self.input_cols])
        except Exception as e:
            print(f"Error extracting state vector: {e}")
            return gains # Zero matrix fallback

        for cv in self.output_cols:
            # Filter context for this CV
            cv_data = self.lime_df[self.lime_df['Output_Name'] == cv]
            
            if cv_data.empty:
                continue
                
            # Extract historical input vectors
            # Columns are named "Input_{feat}"
            input_data_cols = [f"Input_{c}" for c in self.input_cols]
            
            # Check if columns exist
            valid_cols = [c for c in input_data_cols if c in cv_data.columns]
            if len(valid_cols) != len(self.input_cols):
                # Fallback if mismatch
                continue
                
            history_inputs = cv_data[valid_cols].values
            
            # Calculate Euclidean distances
            # (simple, unweighted)
            dists = np.linalg.norm(history_inputs - state_vec, axis=1)
            
            # Find nearest k
            # Using argpartition for efficiency
            if len(dists) <= k:
                nearest_indices = np.arange(len(dists))
            else:
                nearest_indices = np.argpartition(dists, k)[:k]
            
            # Average the gains of nearest neighbors
            nearest_samples = cv_data.iloc[nearest_indices]
            
            for mv in self.input_cols:
                gain_col = f"Gain_{mv}"
                if gain_col in nearest_samples.columns:
                    avg_gain = nearest_samples[gain_col].mean()
                    gains.loc[mv, cv] = avg_gain
                    
        return gains

    def configure(self, mvs, dvs, cvs, objective_formula, objective_goal, objective_weight=10.0):
        self.mvs = mvs
        self.dvs = dvs
        self.cvs = cvs
        self.objective_formula = objective_formula
        self.objective_goal = objective_goal
        self.objective_weight = float(objective_weight)
        
        # Sync to self.config for persistence
        if 'settings' not in self.config: self.config['settings'] = {}
        self.config['settings']['mvs'] = self.mvs
        self.config['settings']['dvs'] = self.dvs
        self.config['settings']['cvs'] = self.cvs
        self.config['settings']['objective_formula'] = self.objective_formula
        self.config['settings']['objective_goal'] = self.objective_goal
        self.config['settings']['objective_weight'] = self.objective_weight

    def get_initial_state(self, current_values):
        """
        Returns state dictionary initialized with current plant values.
        """
        return current_values.copy()

    def step_dmc(self, current_state, delta_mvs):
        """
        Predict next state using DMC linear model with context-aware gains.
        next_cv = current_cv + sum(local_gain * delta_mv)
        """
        next_state = current_state.copy()
        
        # Get Local Gains for current state (Non-linear control)
        K_matrix = self.get_gains(current_state)
        
        # Update MVs in state
        for mv, delta in delta_mvs.items():
            if mv in next_state:
                next_state[mv] += delta
                
        # Update CVs based on gains
        for cv in self.cvs:
            if cv in K_matrix.columns:
                change = 0
                for mv, delta in delta_mvs.items():
                    if mv in K_matrix.index:
                        gain = K_matrix.loc[mv, cv]
                        change += gain * delta
                
                if cv in next_state:
                    next_state[cv] += change
                else:
                    next_state[cv] = change # Should rely on initial state
                        
        # Calculate Objective Function
        # Use simple eval for formula (safe context assumed)
        if self.objective_formula and self.objective_formula.strip():
            try:
                # Create context with variable names
                context = next_state.copy()
                obj_val = eval(self.objective_formula, {}, context)
                next_state['__OBJECTIVE__'] = obj_val
            except Exception as e:
                # print(f"Objective Eval Error: {e}")
                next_state['__OBJECTIVE__'] = 0.0
        else:
             next_state['__OBJECTIVE__'] = 0.0
            
        return next_state

    def calculate_cost(self, state):
        """
        Calculate cost (penalty) for a state based on bounds and goals.
        Lower is better.
        """
        cost = 0.0
        
        # 1. CV Constraints
        for cv, specs in self.cvs.items():
            val = state.get(cv, 0)
            target = specs.get('target', None)
            mn, mx = specs.get('min', -np.inf), specs.get('max', np.inf)
            weight = specs.get('weight', 1.0)
            
            # Bound violation penalties (High weight)
            if val < mn: cost += 100 * weight * (mn - val)**2
            if val > mx: cost += 100 * weight * (val - mx)**2
            
            # Target tracking (Soft constraint)
            if target is not None:
                cost += weight * (val - target)**2
                
        # 2. MV Constraints (Hard bounds usually handled in action generation, but add penalty just in case)
        for mv, specs in self.mvs.items():
            val = state.get(mv, 0)
            mn, mx = specs.get('min', -np.inf), specs.get('max', np.inf)
            if val < mn: cost += 1000 * (mn - val)**2
            if val > mx: cost += 1000 * (val - mx)**2
            
        # 3. Objective Function Optimization
        obj_val = state.get('__OBJECTIVE__', 0)
        obj_weight = self.objective_weight
        
        if self.objective_goal == 'max':
            cost -= obj_val * obj_weight # Negative cost = Reward
        elif self.objective_goal == 'min':
            cost += obj_val * obj_weight
            
        return cost

    def get_legal_actions(self):
        # Generate list of ALL atomic moves
        actions = []
        possible_deltas = [-0.1, 0.0, 0.1]
        for mv in self.mvs:
            for d in possible_deltas:
                actions.append({mv: d})
        return actions

    def search_mcts(self, initial_state, iterations=100, horizon=5):
        """
        Perform MCTS to find best next MV moves.
        """
        legal_actions = self.get_legal_actions()
        root = MCTSNode(state=initial_state, possible_actions=legal_actions)
        
        for _ in range(iterations):
            node = root
            
            # 1. Select
            while node.is_fully_expanded() and not node.is_terminal(horizon):
                node = node.best_child()
                
            # 2. Expand
            if not node.is_fully_expanded() and not node.is_terminal(horizon):
                node = node.expand(self)
                
            # 3. Simulate (Rollout)
            current_rollout_state = node.state
            depth = 0
            # Calculate depth relative to node
            temp_node = node
            current_depth = 0
            while temp_node.parent:
                current_depth += 1
                temp_node = temp_node.parent
                
            steps_remaining = horizon - current_depth
            
            for _ in range(steps_remaining):
                # Random action
                if not legal_actions: break
                random_action = legal_actions[np.random.randint(len(legal_actions))]
                current_rollout_state = self.step_dmc(current_rollout_state, random_action)
                
            # 4. Backpropagate
            cost = self.calculate_cost(current_rollout_state)
            score = -cost # Higher is better
            
            while node is not None:
                node.visits += 1
                node.value += score
                node = node.parent
                
        # Return best immediate action (Robust Child)
        if not root.children:
            return {}
        
        visits = [child.visits for child in root.children]
        best_child = root.children[np.argmax(visits)]
        
        return best_child.action


