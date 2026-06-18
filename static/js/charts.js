const departmentChart =
document.getElementById(
"departmentChart"
);

if(departmentChart){

new Chart(
departmentChart,
{
type:"doughnut",

data:{

labels:[
"Emergency",
"Cardiology",
"Neurology",
"General Medicine"
],

datasets:[
{
data:[
45,
30,
15,
25
]
}
]
}
}
);

}

const patientChart =
document.getElementById(
"patientChart"
);

if(patientChart){

new Chart(
patientChart,
{
type:"line",

data:{

labels:[
"Mon",
"Tue",
"Wed",
"Thu",
"Fri",
"Sat",
"Sun"
],

datasets:[
{
label:"Patients",

data:[
20,
25,
32,
28,
40,
35,
45
]
}
]
}
}
);

}

const emergencyChart =
document.getElementById(
"emergencyChart"
);

if(emergencyChart){

new Chart(
emergencyChart,
{
type:"bar",

data:{

labels:[
"Week 1",
"Week 2",
"Week 3",
"Week 4"
],

datasets:[
{
label:"Emergency Cases",

data:[
12,
18,
10,
22
]
}
]
}
}
);

}
