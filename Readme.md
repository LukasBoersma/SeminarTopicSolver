# Seminar Topic Solver

This script assigns seminar topics to students based on their stated preferences.
The basic scenario that this script was written for: There is a set of students and a set of topics.
Each student needs to get exactly one topic assigned (at least as many topics as there are students are assumed).
Each topic may only be assigned to one or zero students.

Each student can specify a preference for each topic in form of a number 1..n,
where a low number indicates a favored topic and a high number indicates a disliked topic.
It is allowed to leave an arbitrary number of preferences unspecified, but each preference number may only be assigned once.

The script uses scipy.optimize.linear_sum_assignment to minimize the sum over all students of the preference numbers that
correspond to the assigned topics. If the preference number is seen as an "unhappiness" value, we minimize the total unhappiness.

## License

This script is licensed under the [MIT license](License.txt).

## Requirements

* Python 3.7+
* Numpy
* Scipy

## Input format

The script reads a semicolon-separated CSV file containing the students as rows, the topics as columns, and preference values in the cells. The first row and the first columns contain the student and topic names. The file should look like this:

````
X;topic1;topic2\n
student1;preferenceStudent1ForTopic1;...\n
student2;preferenceStudent2ForTopic1;...\n
````

See [example.csv](example.csv) for an actual example file.

## Usage

The script expects the filename of the CSV input as the single positional parameter:

````
python seminar_topic_solver.py /path/to/my_student_preferences.csv
````

## Contact

For questions or feedback, write to mail@lukas-boersma.com.