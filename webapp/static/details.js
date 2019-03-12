$(document).ready(function() {
  //Add more fields group
  $(".addMore").click(function() {
    var fieldHTML =
      '<div class="form-group fieldGroup">' +
      $(".fieldGroupCopy").html() +
      "</div>";
    $("body")
      .find(".fieldGroup:last")
      .after(fieldHTML);
  });

  //Remove fields group
  $("body").on("click", ".remove", function() {
    $(this)
      .parents(".fieldGroup")
      .remove();
  });
});

//Recreate employment history for autofill
function createEmployment(position, company, years, months) {
  var fieldHTML =
    '<div class="form-group fieldGroup">' +
    $(".fieldGroupCopy").html() +
    "</div>";
  $("body")
    .find(".fieldGroup:last")
    .after(fieldHTML);
  data = $("body").find(".fieldGroup:last").find(".card").find(".input-group");
  data.find("select[name='position[]']").val(position);
  data.find("input[name='company[]']").val(company);
  data.find("input[name='jobyears[]']").val(years);
  data.find("input[name='jobmonths[]']").val(months);
}

//Add a new A-Level and select desired candidate expertise in it
function checkALevel(value, expertise) {
    //Remove the A-Level from the select to prevent duplicates
    var select = document.getElementById("aLevel");
    select.options[select.selectedIndex] = null;

    //Locate the outer container for adding
    var container = document.getElementById("aLevelContainer");

    //Create a container for each new A-Level
    var p = document.createElement("p");
    p.id = "p"+value;
    p.setAttribute("style", "margin-top:0.4rem;");

    //Hidden input for processing in back-end
    var nameInput = document.createElement("input");
    nameInput.type = "hidden";
    nameInput.name = "aLevelName[]";
    nameInput.value = value;

    //Create a new select for selecting expertise for each A-Level
    var expertiseInput = document.createElement("select");
    expertiseInput.classList.add("select");
    expertiseInput.setAttribute("style","display: inline-block; width:5rem; margin-top:-5px; border:solid; border-width:0.1rem; border-color:#fbef95");
    expertiseInput.name = "aLevelExpertise[]";

    //Loop through possible grades and add each as an option in the select
    var array = ["A*","A","B","C","D","E","U"];
    for (var i = 0; i < array.length; i++) {
        var option = document.createElement("option");
        //For autofilling, ensure that the candidate's stored grade is selected
        if (array[i] == expertise) {
            option.setAttribute("selected", "selected");
        }
        option.setAttribute("value", array[i]);
        option.text = array[i];
        expertiseInput.appendChild(option);
    }
    //Create button to remove A-Level
    var button = document.createElement("button");
    button.id = "b"+value;
    button.name = value;
    button.setAttribute("onclick", "removeALevel(this.name)");
    button.setAttribute("style", "margin-left: 0.2rem; float:right;");
    button.classList.add("button");
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

//Add a new language and select desiredcandidate expertise in it
function checkLanguage(value, expertise) {
    //Remove the language from the select to prevent duplicates
    var select = document.getElementById("language");
    select.options[select.selectedIndex] = null;

    //Locate the outer container for adding
    var container = document.getElementById("languageContainer");

    //Create a container for each new language
    var p = document.createElement("p");
    p.id = "p"+value;
    p.setAttribute("style", "margin-top:0.4rem;");

    //Hidden input for processing in back-end
    var nameInput = document.createElement("input");
    nameInput.type = "hidden";
    nameInput.name = "languageName[]";
    nameInput.value = value;

    //Create a new select for selecting expertise for each language
    var expertiseInput = document.createElement("select");
    expertiseInput.setAttribute("style","display: inline-block; width:5rem; margin-top:-5px; border:solid; border-width:0.1rem; border-color:#fbef95");
    expertiseInput.name = "languageExpertise[]";

    //Loop through possible expertises and add each as an option in the select
    var array = ["10","9","8","7","6","5","4","3","2","1"];
    for (var i = 0; i < array.length; i++) {
      var option = document.createElement("option");
      //For autofilling, ensure that the candidate's stored expertise is selected
      if (array[i] == expertise) {
          option.setAttribute("selected", "selected");
      }
      option.setAttribute("value", array[i]);
      option.text = array[i];
      expertiseInput.appendChild(option);
    }

    //Create button to remove language
    var button = document.createElement("button");
    button.id = "b"+value;
    button.name = value;
    button.setAttribute("onclick", "removeLanguage(this.name)");
    button.setAttribute("style", "margin-left: 0.2rem; float:right;");
    button.classList.add("button");
    button.innerHTML = 'Remove Language';

    //Add all inputs to inner container and append it to outer container
    p.appendChild(document.createTextNode(value + ": "));
    p.appendChild(nameInput);
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
function checkSkill(value, expertise) {
    //Remove the skill from the select to prevent duplicates
    var select = document.getElementById("skill");
    select.options[select.selectedIndex] = null;

    //Locate the outer container for adding
    var container = document.getElementById("skillContainer");

    //Create a container for each new skill
    var p = document.createElement("p");
    p.id = "p"+value;
    p.setAttribute("style", "margin-top:0.4rem;");

    //Hidden input for processing in back-end
    var nameInput = document.createElement("input");
    nameInput.type = "hidden";
    nameInput.name = "skillName[]";
    nameInput.value = value;

    //Create a new select for selecting expertise for each skill
    var expertiseInput = document.createElement("select");
    expertiseInput.setAttribute("style","display: inline-block; width:5rem; margin-top:-5px;; border:solid; border-width:0.1rem; border-color:#fbef95");
    expertiseInput.name = "skillExpertise[]";

    //Loop through possible expertises and add each as an option in the select
    var array = ["10","9","8","7","6","5","4","3","2","1"];
    for (var i = 0; i < array.length; i++) {
      var option = document.createElement("option");
      //For autofilling, ensure that the candidate's stored expertise is selected
      if (array[i] == expertise) {
          option.setAttribute("selected", "selected");
      }
      option.setAttribute("value", array[i]);
      option.text = array[i];
      expertiseInput.appendChild(option);
    }
    //Create button to remove skill
    var button = document.createElement("button");
    button.id = "b"+value;
    button.name = value;
    button.setAttribute("onclick", "removeSkill(this.name)");
    button.setAttribute("style", "margin-left: 0.2rem; float:right;");
    button.classList.add("button");
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

//Add a new hobby and select desired candidate expertise in it
function checkHobby(value, expertise) {
    //Remove the A-Level from the select to prevent duplicates
    var select = document.getElementById("hobby");
    select.options[select.selectedIndex] = null;

    //Locate the outer container for adding
    var container = document.getElementById("hobbyContainer");

    //Create a container for each new hobby
    var p = document.createElement("p");
    p.id = "p"+value;
    p.setAttribute("style", "margin-top:0.4rem;");

    //Hidden input for processing in back-end
    var nameInput = document.createElement("input");
    nameInput.type = "hidden";
    nameInput.name = "hobbyName[]";
    nameInput.value = value;

    //Create a new select for selecting expertise for each hobby
    var expertiseInput = document.createElement("select");
    expertiseInput.setAttribute("style","display: inline-block; width:5rem; margin-top:-5px;; border:solid; border-width:0.1rem; border-color:#fbef95");
    expertiseInput.name = "hobbyExpertise[]";

    //Loop through possible expertises and add each as an option in the select
    var array = ["10","9","8","7","6","5","4","3","2","1"];
    for (var i = 0; i < array.length; i++) {
      var option = document.createElement("option");
      //For autofilling, ensure that the candidate's stored interest is selected
      if (array[i] == expertise) {
          option.setAttribute("selected", "selected");
      }
      option.setAttribute("value", array[i]);
      option.text = array[i];
      expertiseInput.appendChild(option);
    }

    //Create button to remove hobby
    var button = document.createElement("button");
    button.id = "b"+value;
    button.name = value;
    button.setAttribute("onclick", "removeHobby(this.name)");
    button.setAttribute("style", "margin-left: 0.2rem; float: right;");
    button.classList.add("button");
    button.innerHTML = 'Remove Hobby';

    //Add all inputs to inner container and append it to outer container
    p.appendChild(document.createTextNode(value + ": "));
    p.appendChild(nameInput);
    p.appendChild(expertiseInput);
    p.appendChild(button);
    container.appendChild(p);
}

//Remove the added hobby, and re-add it to the select
function removeHobby(value){
    //Find the container with the hobby in
    var p = document.getElementById("p"+value);
    //Removing the parent element also removes children (select etc.)
    p.parentElement.removeChild(p);
    //Re-add the hobby to the select, now at the end;
    var select = document.getElementById("hobby");
    select.options[select.options.length] = new Option(value, value, false, false);
}
