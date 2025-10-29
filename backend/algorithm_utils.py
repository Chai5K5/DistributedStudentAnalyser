# backend/algorithm_utils.py

# ---------------------------
# Merge Sort Implementation
# ---------------------------
def merge_sort(students, key_index=3):
    """
    Sorts a list of student tuples by a key (default = marks at index 3).
    key_index = 3 corresponds to marks in (roll_no, name, branch, marks, attendance)
    """
    if len(students) <= 1:
        return students

    mid = len(students) // 2
    left = merge_sort(students[:mid], key_index)
    right = merge_sort(students[mid:], key_index)
    return merge(left, right, key_index)

def merge(left, right, key_index):
    sorted_list = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i][key_index] <= right[j][key_index]:
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    return sorted_list


# ---------------------------
# Binary Search Implementation
# ---------------------------
def binary_search(students, roll_no):
    """
    Performs binary search on a list of student tuples sorted by roll_no.
    Returns the student tuple if found, else None.
    """
    low, high = 0, len(students) - 1
    while low <= high:
        mid = (low + high) // 2
        if students[mid][0] == roll_no:
            return students[mid]
        elif students[mid][0] < roll_no:
            low = mid + 1
        else:
            high = mid - 1
    return None
