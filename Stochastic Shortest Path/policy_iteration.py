#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: huiming zhou
"""

import env
import tools
import motion_model

import matplotlib.pyplot as plt
import numpy as np
import copy
import sys


class Policy_iteration:
    def __init__(self, x_start, x_goal):
        self.u_set = motion_model.motions                       # feasible input set
        self.xI, self.xG = x_start, x_goal
        self.e = 0.001                                          # threshold for convergence
        self.gamma = 0.9                                        # discount factor
        self.obs = env.obs_map()                                # position of obstacles
        self.lose = env.lose_map()                              # position of lose states
        self.name1 = "policy_iteration, e=" + str(self.e) \
                     + ", gamma=" + str(self.gamma)
        self.name2 = "convergence of error, e=" + str(self.e)


    def policy_evaluation(self, policy, value):
        """
        Evaluate current policy.

        :param policy: current policy
        :param value: value table
        :return: new value table generated by current policy
        """

        delta = sys.maxsize

        while delta > self.e:           # convergence condition
            x_value = 0
            for x in value:
                if x not in self.xG:
                    [x_next, p_next] = motion_model.move_prob(x, policy[x], self.obs)
                    v_Q = self.cal_Q_value(x_next, p_next, value)
                    v_diff = abs(value[x] - v_Q)
                    value[x] = v_Q
                    if v_diff > 0:
                        x_value = max(x_value, v_diff)
            delta = x_value

        return value


    def policy_improvement(self, policy, value):
        """
        Improve policy using current value table.

        :param policy: policy table
        :param value: current value table
        :return: improved policy table
        """

        for x in value:
            if x not in self.xG:
                value_list = []
                for u in self.u_set:
                    [x_next, p_next] = motion_model.move_prob(x, u, self.obs)
                    value_list.append(self.cal_Q_value(x_next, p_next, value))
                policy[x] = self.u_set[int(np.argmax(value_list))]

        return policy


    def iteration(self):
        """
        polity iteration: using evaluate and improvement process until convergence.
        :return: value table and converged policy.
        """

        value_table = {}
        policy = {}
        count = 0

        for i in range(env.x_range):
            for j in range(env.y_range):
                if (i, j) not in self.obs:
                    value_table[(i, j)] = 0             # initialize value table
                    policy[(i, j)] = self.u_set[0]      # initialize policy table

        while True:
            count += 1
            policy_back = copy.deepcopy(policy)
            value_table = self.policy_evaluation(policy, value_table)       # evaluation process
            policy = self.policy_improvement(policy, value_table)           # policy improvement process
            if policy_back == policy: break                                 # convergence condition

        self.message(count)

        return value_table, policy


    def cal_Q_value(self, x, p, table):
        """
        cal Q_value.

        :param x: next state vector
        :param p: probability of each state
        :param table: value table
        :return: Q-value
        """

        value = 0
        reward = env.get_reward(x, self.xG, self.lose)                  # get reward of next state
        for i in range(len(x)):
            value += p[i] * (reward[i] + self.gamma * table[x[i]])      # cal Q-value

        return value


    def simulation(self, xI, xG, policy):
        """
        simulate a path using converged policy.

        :param xI: starting state
        :param xG: goal state
        :param policy: converged policy
        :return: simulation path
        """

        plt.figure(1)                                               # path animation
        tools.show_map(xI, xG, self.obs, self.lose, self.name1)     # show background

        x, path = xI, []
        while True:
            u = policy[x]
            x_next = (x[0] + u[0], x[1] + u[1])
            if x_next in self.obs:
                print("Collision!")                                 # collision: simulation failed
            else:
                x = x_next
                if x_next in xG:
                    break
                else:
                    tools.plot_dots(x)                              # each state in optimal path
                    path.append(x)
        plt.show()

        return path


    def message(self, count):
        print("starting state: ", self.xI)
        print("goal states: ", self.xG)
        print("condition for convergence: ", self.e)
        print("discount factor: ", self.gamma)
        print("iteration times: ", count)


if __name__ == '__main__':
    x_Start = (5, 5)
    x_Goal = [(49, 5), (49, 25)]

    PI = Policy_iteration(x_Start, x_Goal)
    [value_PI, policy_PI] = PI.iteration()
    path_PI = PI.simulation(x_Start, x_Goal, policy_PI)
