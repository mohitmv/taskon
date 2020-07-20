import collections
import enum


class TaskonError(Exception):
    """General TaskonError"""
    pass

class TaskonFatalError(Exception):
    """
    TaskonFatalError is non recoverable exception and it should not be catched
    """
    pass


class TaskResult:
    """Placeholder for task result."""
    def __init__(self, name):
        self.name = name

class TaskStatus(enum.IntEnum):
    SUCCESS = 1
    FAILURE = 2
    ABORTED = 3
    NOT_EXECUTED = 4


class Object(dict):
    """
    Object extends the inbuilt dictionary and exposes the keys as class members.
    p = Object({"key1": 11, "key2": 22})
    key1 of p can be accessed by p.key1 as well as p["key1"].
    """
    def __init__(self, *initial_value, **kwargs):
        self.__dict__ = self
        dict.__init__(self, *initial_value, **kwargs)

def cycleDetection(nodes, edge_func):
    """
    Given a graph with @nodes, a @edge_func (node -> directly connected nodes),
    Return the Object(cycle_found=False) if there is no cycle in graph.
    Return an Object(cycle_found=True, cycle_path=list-of-nodes-in-cycle) if
    there is some cycle in the graph.
    """
    visited = set()
    ancestors = set()
    ancestors_stack = []
    main_stack = list(nodes)
    main_stack.reverse()
    while len(main_stack) > 0:
        stack_top = main_stack[-1]
        if len(ancestors_stack) > 0 and stack_top == ancestors_stack[-1]:
            visited.add(stack_top)
            ancestors_stack.pop()
            main_stack.pop()
            ancestors.remove(stack_top)
        else:
            ancestors_stack.append(stack_top)
            ancestors.add(stack_top)
            for n in (edge_func(stack_top)):
                if n in visited:
                    continue
                if n in ancestors: # cycle found
                    cycle_path = ancestors_stack[ancestors_stack.index(n):]
                    cycle_path.append(n)
                    return Object(cycle_found=True,
                                  cycle_path=cycle_path)
                else:
                    main_stack.append(n)
    return Object(cycle_found=False)

def depsCover(nodes, edge_func):
    q = collections.deque(nodes)
    visited = set(nodes)
    while len(q) > 0:
        q_top = q.pop()
        for i in edge_func(q_top):
            if i not in visited:
                q.appendleft(i)
                visited.add(i)
    return visited

