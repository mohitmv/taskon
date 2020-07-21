import collections

from taskon.common import Object

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

