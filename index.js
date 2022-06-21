const form = document.getElementById('form');
const formDiv = document.getElementById('formDiv');
const tableDiv = document.getElementById('tableDiv');
const tables = form.elements['numberOfTables'];
const studentList = form.elements['studentList'];
var i = 0;

let nTables;
let students;
let fileText = "";

form.addEventListener('submit', async event => {
    event.preventDefault();

    nTables = form.elements['numberOfTables'].value;
    students = form.elements['studentList'].value;
    students = document.getElementById("studentList").files[0];

    formDiv.style.display = "none";
    tableDiv.style.display = "block";

    // do file stuff here
    let reader = new FileReader();
    reader.addEventListener("loadend", () => {
        fileText += reader.result.split("\n").join("\\n");
        console.log(fileText);
        i++;
    });
    reader.readAsText(students);
});

function getTables()
{
    return nTables;
}

function getFileText()
{
    return fileText;
}

function realPrint(str){
    document.getElementById("tableDiv").innerHTML += str + "<br>";
}

console.log('Check the code out at https://github.com/rjain37/ssp-table-generation');
