//Default end Post two-weeks after today
$(document).ready(function(){
    var today = new Date();
    today.setDate(today.getDate()+14);
    var end = document.getElementById("end");
    end.value = getFormattedDate(today);
    document.getElementById("created").value = getFormattedDate(new Date());
});

//Convert date to DB desired format
function getFormattedDate(todayTime) {
    var month = todayTime.getMonth() + 1;
    var day = todayTime.getDate();
    var year = todayTime.getFullYear();
    //Append 0 to ensure date is in form yyyy-mm-dd
    if (month != "10" || month !="11" || month !="12"){
        month = "0"+month;
    }
    if (parseInt(day) < 10){
        day = "0"+day;
    }
    var formatted = year + "-" + month + "-" + day;
    return formatted;
}

//Add a new role and select candidate's experience in it
function checkPosition(value) {
    //Remove the role from the select to prevent duplicates
    var select = document.getElementById("position");
    select.options[select.selectedIndex] = null;

    //Locate the outer container for adding
    var container = document.getElementById("positionContainer");

    //Create a container for each new role
    var p = document.createElement("p");
    p.id = "p"+value;
    p.classList.add("mb085");

    //Hidden input for processing in back-end
    var name = document.createElement("input");
    name.type = "hidden";
    name.name = "positionName[]";
    name.value = value;

    //Create input element for years in position
    var yearInput = document.createElement("input");
    yearInput.classList.add("input");
    yearInput.classList.add("nudgeUp");
    yearInput.classList.add("ib");
    yearInput.classList.add("has-text-right");
    yearInput.type="number";
    yearInput.name = "positionYear[]";
    yearInput.setAttribute("onkeyup","if(this.value > 80) this.value = 80;");
    yearInput.id = value;
    yearInput.min = 0;
    yearInput.max = 80;
    yearInput.required = true;

    //Create input element for months in position
    var monthInput = document.createElement("input");
    monthInput.classList.add("input");
    monthInput.classList.add("nudgeUp");
    monthInput.classList.add("ib");
    monthInput.classList.add("has-text-right");
    monthInput.type="number";
    monthInput.name = "positionMonth[]";
    monthInput.setAttribute("onkeyup","if(this.value > 11) this.value = 11;");
    monthInput.id = value;
    monthInput.min = 0;
    monthInput.max = 11;
    monthInput.required = true;

    //Create button to remove position
    var button = document.createElement("button");
    button.id = "b"+value;
    button.name = value;
    button.setAttribute("onclick", "removePosition(this.name)");
    button.classList.add("button");
    button.classList.add("nudgeUp");
    button.classList.add("fieldButton");
    button.innerHTML = 'Remove Position';

    //Add all inputs to inner container and append it to outer container
    p.append(name);
    p.appendChild(document.createTextNode(value + ": "));
    p.appendChild(yearInput);
    p.appendChild(document.createTextNode(" Year(s)"));
    p.appendChild(monthInput);
    p.appendChild(document.createTextNode(" Month(s)"));
    p.appendChild(button);
    container.appendChild(p);
}

//Remove the added role, and re-add the position to the select
function removePosition(value){
    //Find the container with the role in
    var p = document.getElementById("p"+value);
    //Removing the parent element also removes children (select etc.)
    p.parentElement.removeChild(p);
    //Re-add the position to the select, now at the end
    var select = document.getElementById("position");
    select.options[select.options.length] = new Option(value, value, false, false);
}

//Add a new language and select desiredcandidate expertise in it
function checkLanguage(value) {
    //Remove the language from the select to prevent duplicates
    var select = document.getElementById("language");
    select.options[select.selectedIndex] = null;

    //Locate the outer container for adding
    var container = document.getElementById("languageContainer");

    //Create a container for each new language
    var p = document.createElement("p");
    p.id = "p"+value;
    p.classList.add("mb04");

    //Hidden input for processing in back-end
    var nameInput = document.createElement("input");
    nameInput.type = "hidden";
    nameInput.name = "language[]";
    nameInput.value = value;

    //Create a new select for selecting expertise for each language
    var expertiseInput = document.createElement("select");
    expertiseInput.classList.add("ib");
    expertiseInput.classList.add("nudgeUp");
    expertiseInput.name = "languageExpertise[]";
    expertiseInput.id = value;
    //Loop through possible expertises and add each as an option in the select
    var array = ["10","9","8","7","6","5","4","3","2","1"];
    for (var i = 0; i < array.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", array[i]);
        option.text = array[i];
        expertiseInput.appendChild(option);
    }

    //Create button to remove language
    var button = document.createElement("button");
    button.id = "b"+value;
    button.name = value;
    button.setAttribute("onclick", "removeLanguage(this.name)");
    button.classList.add("button");
    button.classList.add("nudgeUp");
    button.classList.add("fieldButton");
    button.innerHTML = 'Remove Language';

    //Add all inputs to inner container and append it to outer container
    p.append(nameInput);
    p.appendChild(document.createTextNode(value + ": "));
    p.appendChild(expertiseInput);
    p.appendChild(button);
    container.appendChild(p);
}

//Remove the added language, and re-add it to the select
function removeLanguage(value){
    //Find the container with the language in
    var p = document.getElementById("p"+value);
    //Removing the parent element also removes children (select etc.)
    p.parentElement.removeChild(p);
    //Re-add the language to the select, now at the end
    var select = document.getElementById("language");
    select.options[select.options.length] = new Option(value, value, false, false);
}

//Add a new skill and select desired candidate expertise in it
function checkSkill(value) {
    //Remove the skill from the select to prevent duplicates
    var select = document.getElementById("skill");
    select.options[select.selectedIndex] = null;

    //Locate the outer container for adding
    var container = document.getElementById("skillContainer");

    //Create a container for each new skill
    var p = document.createElement("p");
    p.id = "p"+value;
    p.classList.add("mb04");

    //Hidden input for processing in back-end
    var nameInput = document.createElement("input");
    nameInput.type = "hidden";
    nameInput.name = "skillName[]";
    nameInput.value = value;

    //Create a new select for selecting expertise for each skill
    var expertiseInput = document.createElement("select");
    expertiseInput.classList.add("ib");
    expertiseInput.classList.add("nudgeUp");
    expertiseInput.name = "skillExpertise[]";
    expertiseInput.id = value;
    //Loop through possible expertises and add each as an option in the select
    var array = ["10","9","8","7","6","5","4","3","2","1"];
    for (var i = 0; i < array.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", array[i]);
        option.text = array[i];
        expertiseInput.appendChild(option);
    }

    //Create button to remove skill
    var button = document.createElement("button");
    button.id = "b"+value;
    button.name = value;
    button.setAttribute("onclick", "removeSkill(this.name)");
    button.classList.add("button");
    button.classList.add("nudgeUp");
    button.classList.add("fieldButton");
    button.innerHTML = 'Remove Skill';

    //Add all inputs to inner container and append it to outer container
    p.appendChild(document.createTextNode(value + ": "));
    p.appendChild(nameInput);
    p.appendChild(expertiseInput);
    p.appendChild(button);
    container.appendChild(p);
}

//Remove the added skill, and re-add it to the select
function removeSkill(value){
    //Find the container with the skill in
    var p = document.getElementById("p"+value);
    //Removing the parent element also removes children (select etc.)
    p.parentElement.removeChild(p);
    //Re-add the skill to the select, now at the end
    var select = document.getElementById("skill");
    select.options[select.options.length] = new Option(value, value, false, false);
}

//Add a new A-Level and select desired candidate grade in it
function checkALevel(value) {
    //Remove the A-Level from the select to prevent duplicates
    var select = document.getElementById("aLevel");
    select.options[select.selectedIndex] = null;

    //Locate the outer container for adding
    var container = document.getElementById("aLevelContainer");

    //Create a container for each new A-Level
    var p = document.createElement("p");
    p.id = "p"+value;
    p.classList.add("mb04");

    //Hidden input for processing in back-end
    var nameInput = document.createElement("input");
    nameInput.type = "hidden";
    nameInput.name = "aLevelName[]";
    nameInput.value = value;

    //Create a new select for selecting expertise for each A-Level
    var expertiseInput = document.createElement("select");
    expertiseInput.classList.add("ib");
    expertiseInput.classList.add("nudgeUp");
    expertiseInput.name = "aLevelExpertise[]";

    //Loop through possible grades and add each as an option in the select
    var array = ["A*","A","B","C","D","E","U"];
    for (var i = 0; i < array.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", array[i]);
        option.text = array[i];
        expertiseInput.appendChild(option);
    }

    //Create button to remove A-Level
    var button = document.createElement("button");
    button.id = "b"+value;
    button.name = value;
    button.setAttribute("onclick", "removeALevel(this.name)");
    button.classList.add("button");
    button.classList.add("nudgeUp");
    button.classList.add("fieldButton");
    button.innerHTML = 'Remove A-Level';

    //Add all inputs to inner container and append it to outer container
    p.appendChild(document.createTextNode(value + ": "));
    p.appendChild(nameInput);
    p.appendChild(expertiseInput);
    p.appendChild(button);
    container.appendChild(p);
}

//Remove the added A-Level, and re-add it to the select
function removeALevel(value){
    //Find the container with the A-Level in
    var p = document.getElementById("p"+value);
    //Removing the parent element also removes children (select etc.)
    p.parentElement.removeChild(p);
    //Re-add the A-Level to the select, now at the end;
    var select = document.getElementById("aLevel");
    select.options[select.options.length] = new Option(value, value, false, false);
}
