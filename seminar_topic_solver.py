helptext="""
    This script assigns seminar topics to students based on their stated preferences.
    The basic scenario that this script was written for: There is a set of students and a set of topics.
    Each student needs to get exactly one topic assigned (at least as many topics as there are students are assumed).
    Each topic may only be assigned to one or zero students.
    
    Each student can specify a preference for each topic in form of a number 1..n,
    where a low number indicates a favored topic and a high number indicates a disliked topic.
    It is allowed to leave an arbitrary number of preferences unspecified, but each preference number may only be assigned once.
    
    The script uses scipy.optimize.linear_sum_assignment to minimize the sum over all students of the preference numbers that
    correspond to the assigned topics. If the preference number is seen as an "unhappiness" value, we minimize the total unhappiness.
    
    CSV format:
    X;topic1;topic2\\n
    student1;preferenceStudent1ForTopic1;...\\n
    student2;preferenceStudent2ForTopic1;...\\n
"""

import re
import csv
import scipy.optimize
import numpy as np
import argparse

# ===========================================
# Configuration
# ===========================================

# Students are expected to give this minimum number of preferences.
# Introduces a slight penalty for students specifying fewer topics.
penalize_below_n_preferences = 3

# ===========================================
# Solver
# ===========================================

def solve_assignment_problem(students, topics, preferences):

    # Build a matrix of preference values
    cost_matrix = np.zeros((len(students), len(topics)))
    for preference_item in preferences:
        (student, topic, cost) = preference_item
        cost_matrix[student, topic] = cost

    # Throw the matrix into the scipy solver
    # (the preference values equal the "cost" that this solver minimizes)
    solution = scipy.optimize.linear_sum_assignment(cost_matrix)

    # Extract the solution from the solver.
    # The solver gives two lists of the row and column indinces.
    # Indices at the same list positions are matched.
    row_indices, col_indices = solution

    # Calculate cost statistics
    total_cost = cost_matrix[row_indices, col_indices].sum()
    print("Total cost: %d" % total_cost)
    average_cost = (total_cost / len(students))
    print("Average cost: %.2f" % average_cost)
    
    if average_cost > penalize_below_n_preferences:
        print("WARNING! Average cost (%.2f) is higher than penalize value (%d). This indicates a bad solution." % (average_cost, penalize_below_n_preferences))

    print("Solution: ")
    for i in range(len(row_indices)):
        student_index = row_indices[i]
        topic_index = col_indices[i]
        print("Student %s gets topic %s" % (students[student_index], topics[topic_index]))

def parse_csv(filename):

    fields = []

    # Read the csv file
    with open(filename, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            fields.append(row)

    # Topic list is in the first row, minus first column
    topics = fields[0][1:]

    # Student list is in the first column, minus first row
    students = [row[0] for row in fields[1:]]

    preferences = []
    
    # For each student, there is a list of unspecified and specified preferences.
    # unspecified_preferences is a list of lists of topic indices
    unspecified_preferences = [[] for i in students]

    # specified_preferences is a list of lists of tuples (topic_index, preference)
    specified_preferences = [[] for i in students]

    # Read specified and unspecified preferences, save them in separate lists
    for student in range(len(students)):
        for topic in range(len(topics)):
            preference_string = fields[student+1][topic+1]
            if preference_string == "":
                unspecified_preferences[student].append(topic)
            else:
                # Convert preference value string into a number
                p = int(preference_string)

                # Make sure the preference value is sane (at least 1 and unique per student)
                if p < 1:
                    raise ValueError("Preference value '%d' of student %s for topic %s was less than one, which is not allowed." % (p, students[student], topics[topic]))
                if p in [q for (t,q) in specified_preferences[student]]:
                    raise ValueError("Preference value '%d' of student %s for topic %s is not unique, which is not allowed." % (p, students[student], topics[topic]))

                specified_preferences[student].append((topic, p))
    
    # Make sure specified preferences are a 1..n sequence for each student
    for student in range(len(students)):
        preference_sum = sum([q for (t,q) in specified_preferences[student]])
        preference_count = len(specified_preferences[student])
        expected_preference_sum = preference_count * (preference_count + 1) / 2
        if expected_preference_sum != preference_sum:
            raise ValueError("Preference values for student %s are not a sequence from 1 to n. The preferences do not start at 1 or the sequence has gaps." % students[student])

    # Assign preference values to the unspecified preferences
    # and merge everything into a preference list
    for student in range(len(students)):
        # When no preferences were given at all by this student, specify this preference value for all topics
        preference_value_for_unspecified = penalize_below_n_preferences + 1

        if len(specified_preferences[student]) > 0:
            # If some preferences were given, unspecified preferences are
            # assigned the maximum assigned preference plus the penalizing value.
            max_preference = max([p for (t,p) in specified_preferences[student]])
            preference_value_for_unspecified = max_preference + penalize_below_n_preferences
        for unspecified_topic in unspecified_preferences[student]:
            specified_preferences[student].append((unspecified_topic, preference_value_for_unspecified))
        for (topic, preference) in specified_preferences[student]:
            preferences.append((student, topic, preference))
    
    return students, topics, preferences

# ===========================================
# Command line parsing
# ===========================================

# Setup command line options
parser = argparse.ArgumentParser(description=helptext, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("input_filename")
parser.add_argument(
    "--penalize_below_n_preferences",
    action="store",
    type=int,
    default=3,
    help="Students are expected to give this minimum number of preferences. Introduces a slight penalty for students specifying fewer topics. Default is 3."
    )

# Parse command line options
args = parser.parse_args()
penalize_below_n_preferences = args.penalize_below_n_preferences
input_filename = args.input_filename

# Execute solver based on command line options
students, topics, preferences = parse_csv(input_filename)
solve_assignment_problem(students, topics, preferences)