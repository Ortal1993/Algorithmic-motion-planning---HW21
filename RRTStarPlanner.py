import numpy as np
from RRTTree import RRTTree
import time

#our import
import RRTPlanner

class RRTStarPlanner(object):

    def __init__(self, planning_env, ext_mode, goal_prob, k):

        # set environment and search tree
        self.planning_env = planning_env
        self.tree = RRTTree(self.planning_env)

        # set search params
        self.ext_mode = ext_mode
        self.goal_prob = goal_prob
        self.k = k

    def plan(self):
        '''
        Compute and return the plan. The function should return a numpy array containing the states (positions) of the robot.
        '''
        start_time = time.time()

        # initialize an empty plan.
        plan = []

        # TODO: Task 4.4
        self.tree.add_vertex(self.planning_env.start)
        start_state = self.planning_env.start
        goal_state = self.planning_env.goal

        while not self.tree.is_goal_exists(goal_state): #how does the number of samples is determined?
            state_rand = sample_random(self.goal_prob, self.planning_env, self.planning_env.goal)
            _, state_near = self.tree.get_nearest_state(state_rand)
            state_new = self.extend(state_near, state_rand)
            if self.planning_env.edge_validity_checker(state_near, state_new):
                v_near_id = self.tree.get_idx_for_state(state_near)
                v_new_id = self.tree.add_vertex(state_new)
                
                dist = self.planning_env.compute_distance(state_near, state_new)
                self.tree.add_edge(v_near_id, v_new_id, dist)

                _, k_nearest_states = self.tree.get_k_nearest_neighbors(state_new, self.k)
                

                for state_potential_father in k_nearest_states:
                    self.rewire(state_new, state_potential_father)

                for state_potential_child in k_nearest_states:
                    self.rewire(state_potential_child, state_new)

        #constructing the plan from the goal to the start
        curr_id = self.tree.get_idx_for_state(goal_state)
        start_id = self.tree.get_idx_for_state(start_state)#should be 0 always
        while (curr_id != start_id):
            plan.append(self.tree.vertices[curr_id].state)
            curr_id = self.tree.edges[curr_id]

        plan.append(start_state)
        
        # print total path cost and time
        print('Total cost of path: {:.2f}'.format(self.compute_cost(plan)))
        print('Total time: {:.2f}'.format(time.time()-start_time))

        return np.array(plan)

    def compute_cost(self, plan):
        '''
        Compute and return the plan cost, which is the sum of the distances between steps.
        @param plan A given plan for the robot.
        '''
        # TODO: Task 4.4
        cost = 0.0
        for i in range(len(plan) - 1):
            cost += self.planning_env.compute_distance(plan[i], plan[i + 1])
        return cost

    def extend(self, near_state, rand_state):
        '''
        Compute and return a new position for the sampled one.
        @param near_state The nearest position to the sampled position.
        @param rand_state The sampled position.
        '''
        # TODO: Task 4.4
        if self.ext_mode == "E2":
            step_size = 0.3
            dist = self.planning_env.compute_distance(near_state, rand_state)
            if step_size > dist:
                return rand_state            
            intervals = int(np.ceil(dist / step_size))
            new_states = np.linspace(near_state, rand_state, intervals)
            rand_state = new_states[1]

        return rand_state
    
    #our function
    def rewire(self, child, father):
        if self.planning_env.edge_validity_checker(father, child):
            cost_new_edge = self.planning_env.compute_distance(father, child)
            cost_father = self.tree.get_vertex_for_state(father).cost

            cost_child = self.tree.get_vertex_for_state(child).cost
            if cost_new_edge + cost_father < cost_child:
                id_father = self.tree.get_idx_for_state(father)
                id_child = self.tree.get_idx_for_state(child)

                self.tree.edges[id_child] = id_father
                self.tree.get_vertex_for_state(child).set_cost(cost_new_edge + cost_father)

    
#our function
def sample_random(goal_prob, env, goal) -> np.array:
    if np.random.rand() < goal_prob:
        return goal
    else:# With probability 1 - p_bias, sample randomly within joint limits
        x = np.random.uniform(env.xlimit[0], env.xlimit[1])
        y = np.random.uniform(env.ylimit[0], env.ylimit[1])
        while not env.state_validity_checker((x, y)):
            x = np.random.uniform(env.xlimit[0], env.xlimit[1])
            y = np.random.uniform(env.ylimit[0], env.ylimit[1])   
        return np.array((x, y))