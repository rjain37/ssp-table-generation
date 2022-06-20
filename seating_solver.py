ID_NAME = {}

def make_people(filename):
    file = open(filename, "r")
    people = file.read().splitlines()
    for i in range(len(people)):
        people[i] = people[i].split(", ")
        ID_NAME[i] = people[i][0]
        people[i] = i, int(people[i][1]), int(people[i][2]) - 1
    groups = [[0 for i in range(1)] for j in range(12)]
    for i in range(len(people)):
        groups[people[i][2]].append(people[i][0])
    for i in range(len(groups)):
        del groups[i][0]
    for i in range(len(people)):
        for j in groups[people[i][2]]:
            if j != people[i][0]:
                people[i] = list(people[i])
                people[i].append(j)
    for i in range(len(people)):
        del people[i][0]
        del people[i][1]
    return people

make_people("TableAssign/roamers.txt")
print(people)
