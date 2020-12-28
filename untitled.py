import database as db
from datetime import date
import re
import heapq





def get_indices_of_max_3_in_list(a):
    largest_3 = []
    for i in range(3):
        largest_3.append(sorted(a, reverse=True)[i])
    indices = []
    for i in largest_3:
        indices.append(a.index(i))
    return indices


a = [2, 0, 3, 1, 5, 3, 7, 0, 1, 2, 1]
b = heapq.nlargest(3, list(range((len(a)))), key=a.__getitem__)
c = heapq.nlargest(3, a)
print(b)
print(c)


