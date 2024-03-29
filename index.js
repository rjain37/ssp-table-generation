// <!doctype html>
// <html lang = "en">
//     <head>
//         <title>
//             SSP Table Generation
//         </title>

//         <meta charset="UTF-8">
//         <meta name="viewport" content="width=device-width, initial-scale=1.0" />

//         <!--handmade stuff-->
//         <link rel="stylesheet" href="style.css">

//         <!--jquery-->
//         <script src="https://code.jquery.com/jquery-3.5.1.min.js"
//         integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0=" crossorigin="anonymous"></script>

//         <!--bootstrap-->
//         <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
//         <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
    
//         <!--pyscript-->
//         <link rel="stylesheet" href="https://pyscript.net/alpha/pyscript.css" />
//         <script defer src="https://pyscript.net/unstable/pyscript.js"></script>
//     </head>

//     <body>
//         <div class = "container" style = "display: flex; justify-content: center;">
//             <a href = "/"><img src="logo.jpg" alt="SSP Logo" height = "112" width = "200"></a>
//         </div>

//         <div class = "container border big" style = "display: block;" id = "formDiv">
//             <form method = "POST" id = "form">
//                 <div class="form-group">
//                   <label for="numberOfTables">Number of Tables</label>
//                   <input type="number" class="form-control" id="numberOfTables" aria-describedby="numberOfTables" placeholder="Number of Tables as an integer">
//                 </div>
//                 <div class="form-group">
//                     <label for="studentList">List of Students with name, sex, group number (example file <a href = "example.txt">here</a>)</label>
//                     <input type="file" class="form-control" id="studentList" aria-describedby="studentList" placeholder="Student list as a .txt file">
//                 </div>
//                 <button type="submit" class="btn btn-primary">Submit</button>
//               </form>
//         </div>

//         <py-config>
//             packages = ["numpy", "scipy"]
//         </py-config>

//         <py-script>
//             import js
//             from scipy.optimize import quadratic_assignment
//             import numpy as np
//             from math import ceil
//             from pyodide import create_proxy

//             def make_people(filename):
//                 file = open(filename, "r")
//                 people = file.read().splitlines()
//                 for i in range(len(people)):
//                     people[i] = people[i].split(", ")
//                     ID_NAME[i] = people[i][0]
//                     people[i] = i, int(people[i][1]), int(people[i][2]) - 1
//                 groups = [[0 for i in range(1)] for j in range(12)]
//                 for i in range(len(people)):
//                     groups[people[i][2]].append(people[i][0])
//                 for i in range(len(groups)):
//                     del groups[i][0]
//                 for i in range(len(people)):
//                     for j in groups[people[i][2]]:
//                         if j != people[i][0]:
//                             people[i] = list(people[i])
//                             people[i].append(j)
//                 for i in range(len(people)):
//                     del people[i][0]
//                     del people[i][1]
//                 return people
            
//             def run(self):
//                 #Create a 2D array for people. Each entry is of the form[sex, group_id1, group_id2]
//                 #Female = 1, Male = 0
//                 number_of_predictions = 6
//                 ID_NAME = {}
//                 people = []

//                 # peopleFileText = "Sarim, 0, 1\nSabrina, 1, 2\nKyra, 1, 3\nSavar, 0, 4\nSam, 0, 1\nFernanda, 1, 4\nSrijan, 0, 3\nGabriele, 0, 5\nCeline, 1, 6\nRyan F., 0, 11\nRyan E., 0, 10\nNatalie, 1, 11\nLucy K., 1, 2\nNavit, 0, 3\nArthur, 0, 7\nJD, 0, 9\nJosiah, 0, 7\nDrew, 0, 9\nRohan, 0, 12\nAntonio, 0, 10\nSonia, 1, 1\nLucy G., 1, 12\nAi-Dan, 1, 7\nSophie, 1, 8\nOliver, 0, 5\nCalvin, 0, 6\nFer, 1, 6\nVicki, 1, 10\nDipakshi, 1, 12\nRia, 1, 8\nKai, 0, 2\nVictoria, 1, 11\nNico, 0, 8\nVicky, 1, 5\nMegan, 1, 9\nMoer, 1, 4"
//                 peopleFileText = js.getFileText()
//                 file = open("people.txt", "w")
//                 file.write(peopleFileText)
//                 file.close()
//                 file = open("people.txt", "r")
//                 people = file.read().splitlines()
//                 for i in range(len(people)):
//                     people[i] = people[i].split(", ")
//                     ID_NAME[i] = people[i][0]
//                     people[i] = i, int(people[i][1]), int(people[i][2]) - 1
//                 groups = [[0 for i in range(1)] for j in range(12)]
//                 for i in range(len(people)):
//                     groups[people[i][2]].append(people[i][0])
//                 for i in range(len(groups)):
//                     del groups[i][0]
//                 for i in range(len(people)):
//                     for j in groups[people[i][2]]:
//                         if j != people[i][0]:
//                             people[i] = list(people[i])
//                             people[i].append(j)
//                 for i in range(len(people)):
//                     del people[i][0]
//                     del people[i][1]

//                 # people = make_people("example.txt")

//                 NUM_ROAMERS = len(people)
//                 NUM_TABLES = int(js.getTables())

//                 #Create a distance matrix for the quadratic assignment problem
//                 table_distance_matrix = np.zeros((NUM_ROAMERS, NUM_ROAMERS))

//                 #We can imagine table_distance_matrix as a collection of seats, each of which
//                 #has some connection weight with each other.
//                 #Seats at the same table should have weight 1. Seats at different tables should have weight zero.
//                 remaining_roamers = NUM_ROAMERS
//                 remaining_tables = NUM_TABLES
//                 startex = 0
//                 for i in range(NUM_TABLES):
//                     people_per_table = ceil(remaining_roamers/remaining_tables)
//                     endex = people_per_table + startex
//                     remaining_tables -= 1
//                     remaining_roamers -= people_per_table
//                     table_distance_matrix[startex:endex,startex:endex] = 1
//                     startex += people_per_table


//                 #Before we make a familiarity matrix (explained below), we want two helper methods
//                 #First, we want a method that can increment directional weights of a matrix given a list.
//                 def update_familiarity(id, connection_ids, weight_increment):
//                     for person_id in connection_ids:
//                         familiarity_matrix[id, person_id] += weight_increment
//                     return True

//                 #Second, we want to initialize lists of genders. These lists will be passed into update_familiarity
//                 #to establish assumed familiarity between same genders. This can be a method or just a code block
//                 females = [] 
//                 males = []
//                 for i in range(len(people)):
//                     if(people[i][0] == 1):
//                         females.append(i)
//                     elif(people[i][0] == 0):
//                         males.append(i)

//                 #Now we want a familiarity matrix. Familiarity is where we take inputs like sex, previous seating, groups, etc.
//                 #The quadratic_assignment method minimizes the "fun," a metric found by adding together all the
//                 #familiarity*distances (not matrix multiplication, term-wise multiplication)
//                 familiarity_matrix = np.zeros((NUM_ROAMERS, NUM_ROAMERS))
//                 for i in range(len(people)):
//                     #Make everyone familiar with their sex. This is arguably the most important determinator because
//                     #It is very easy for people to notice when tables are mismatched, especially compared to other metrics
//                     #We wouldn't to cause an uproar now would we :). That's why the weight of gender is 20
//                     if(i in females):
//                         update_familiarity(i, females, 20)
//                     elif(i in males):
//                         update_familiarity(i, males, 20)
//                     #Make people familiar with people in their group.
//                     update_familiarity(i, people[i][1:],5)


//                 #Now we want to manage how many groups we want to create
//                 current_week = 1
//                 for i in range(number_of_predictions):
//                     #Reset main diagonal to zero. This seems important for the optimization algorithm.
//                     #Main diagonal could be changed by "sitting at the same table" and "being the same sex" as yourself.
//                     for i in range(NUM_ROAMERS):
//                         familiarity_matrix[i,i] = 0
//                     #Make the assignments. The algorithm is blackbox but know that 2opt is more accurate than the default
//                     #Basically, take in distance and flow (familiarity) matrices and minimizes the fun value (objective function)
//                     #fun is calculated by summing the term-wise multiplication of distance and flow
//                     res = quadratic_assignment(table_distance_matrix, familiarity_matrix, method = '2opt')
//                     res = res.col_ind
//                     #res is just a 1D array of all the people, we still need to bring back the structure of tables
//                     #Create a list of all the people at the table to update their familiarities (and print them out)
//                     #This table code should be familiar. We used the same algorithm to create the table_distance_matrix
//                     #which was where we first implemented the table concept to begin with.
//                     remaining_roamers = NUM_ROAMERS
//                     remaining_tables = NUM_TABLES
//                     #Note that table_array is a list, not an array. We need its size to be mutable
//                     table_list = []
//                     index = 0
                    
//                     for i in range(NUM_TABLES):
//                         people_per_table = ceil(remaining_roamers/remaining_tables)
//                         remaining_roamers -= people_per_table
//                         remaining_tables -= 1
//                         table_list.append([None]*people_per_table)
//                         for j in range(people_per_table):
//                             table_list[i][j] = res[index]
//                             index += 1

//                     #DON'T DELETE OR OPEN OR LOOK OR READ OR COPY
//                     def ignore():
//                         # what was here?!?!?
//                         return None

//                     #Now start printing Assignments
//                     if current_week == 1:
//                         ID_NAME[0] = "xx" + ID_NAME[0]
//                     js.realPrint("Week " + str(current_week) + " Assignments")
//                     current_table = 1
//                     for table in table_list:
//                         js.realPrint("Table " + str(current_table) + ": ", end = '')
//                         for person in table:
//                             js.realPrint(ID_NAME[person][2:] + ' ', end='')
//                         js.realPrint("")
//                         current_table += 1

//                     #Now we update the familiarity matrix with last week's table assignments
//                     #Don't worry about "becoming familiar with yourself." 
//                     #We're setting it back to zero at the top of the overarching loop!
//                     for table in table_list:
//                         for person in table_list:
//                             update_familiarity(person, table, 3)
//                     current_week += 1
//         </py-script>

//         <div class = "container border big" style = "display: none;" id = "tableDiv">
//             <button type="button" id="button" class = "btn btn-primary" pys-onClick = "run">Display Tables</button>
//             <br>
//         </div>

//         <script src="index.js"></script>
//     </body>

//     <footer class="text-center text-dark p-3 fixed-bottom" style="background-color: #f1f1f1;">
//         Created by Oliver Lin, Rohan Jain, Gabriel di Gianluca, and Nico von Eckenberg of <a href = "https://summerscience.org/category/ssp-blogs/2022/ssp22unc/" >SSP UNC 2022.</a>
//         <br>
//     </footer>
// </html>
