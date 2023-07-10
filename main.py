import numpy as np
import pandas as pd
import heapq
from dataclasses import dataclass, field

TO_MIN_BY_TRAIN = 60 / 30
CHANGE_LINE_MIN = 4

class TrainSystem:
    def __init__(self):
        self.edge_distances = pd.read_csv("edge_distances.csv").fillna(float("inf"))
        self.edge_weights = self.edge_distances.to_numpy() * TO_MIN_BY_TRAIN
        self.straight_line_distances = pd.read_csv("straight_line_distances.csv")
        self.straight_line_times = self.straight_line_distances.to_numpy() * TO_MIN_BY_TRAIN
        self.lines = {
            "red": [3, 9, 11, 13], 
            "green": [4, 8, 12, 13, 14], 
            "blue": [1, 2, 3, 4, 5, 6], 
            "yellow": [2, 5, 7, 8, 9, 10]
        }
        
    def print(self):
        print(self.edge_weights)
        print(self.straight_line_times)
        
    def get_edge(self, s1, s2):
        if s1 > s2:
            s1, s2 = s2, s1
        return self.edge_weights[s1 - 1, s2 - 1]
    
    def get_ETA_goal(self, station, goal):
        s, g = station, goal
        if s > g:
            g, s = s, g
        return self.straight_line_times[s - 1, g - 1]
    
    def get_lines(self, station):
        st_lines = []
        for line in self.lines:
            if station in self.lines[line]:
                st_lines.append(line)

        return st_lines
    
    def get_neighbors(self, station):
        neighbors = []
        for i in range(1, 14 + 1):
            if self.get_edge(station, i) != float("inf"):
                neighbors.append(i)
        return neighbors


class PriorityQueue:
    def __init__(self):
        self.elements = {}
    
    def push(self, item, priority):
        self.elements[item] = priority
    
    def pop(self):
        idx = np.argmin(list(self.elements.values()))
        top = list(self.elements.keys())[idx]
        
        del self.elements[top]
        return top
    
class Station:
    color_mapping = {
        "blue": '\033[94m',
        "green": '\033[92m',
        "yellow": '\033[93m',
        "red": '\033[91m'
    }
    ENDC = '\033[0m'

    def __init__(self, number: int, line: str):
        self.number = number
        self.line = line

    def __str__(self):
        return f"{self.color_mapping[self.line]}{self.number}{self.ENDC}"

def search(graph, start, goal):
    precedents = {start: None}
    minutes_since_start = {start: 0}
    
    frontier = PriorityQueue()
    frontier.push(start, 0)
    
    while len(frontier.elements) > 0:
        print(frontier.elements)
        current = frontier.pop()
        
        if current == goal:
            break
        
        for neighbor in graph.get_neighbors(current):
            elapsed_time = minutes_since_start[current] + graph.get_edge(current, neighbor)
            if neighbor not in minutes_since_start or elapsed_time < minutes_since_start[neighbor]:
                minutes_since_start[neighbor] = elapsed_time
                frontier.push(neighbor, elapsed_time + graph.get_ETA_goal(neighbor, goal))
                precedents[neighbor] = current
    
    return precedents, minutes_since_start

def route_from_precedents(start, goal, precedents, times):
    current = goal
    route = []
    
    if goal in precedents:
        while current != start:
            route.append(current)
            current = precedents[current]
    route.append(start)
    route.reverse()
    return route, np.round(times[goal], 5)

if __name__ == "__main__":
    ts = TrainSystem()
    S, F = 1, 14
    precedents, elapsed_times = search(ts, S, F)
    route, final_ETA = route_from_precedents(S, F, precedents, elapsed_times)
    print(route)
    print(final_ETA)