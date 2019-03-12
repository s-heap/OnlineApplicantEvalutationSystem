//Hide irrelevant tabs' content and show the clicked one's content,
//adding the is-active class to the tab itself so that it appears selected
function showNumeracy() {
    $("#numeracy").show();
    $("#numTab").addClass("is-active");
    $("#literacy").hide();
    $("#litTab").removeClass("is-active");
    $("#abstract").hide();
    $("#absTab").removeClass("is-active");
    $("#situational").hide();
    $("#sitTab").removeClass("is-active");
    $("#next").show();
    $("#submit").hide();
}
function showLiteracy() {
    $("#literacy").show();
    $("#litTab").addClass("is-active");
    $("#numeracy").hide();
    $("#numTab").removeClass("is-active");
    $("#abstract").hide();
    $("#absTab").removeClass("is-active");
    $("#situational").hide();
    $("#sitTab").removeClass("is-active");
    $("#next").show();
    $("#submit").hide();
}
function showAR() {
    $("#abstract").show();
    $("#absTab").addClass("is-active");
    $("#numeracy").hide();
    $("#numTab").removeClass("is-active");
    $("#literacy").hide();
    $("#litTab").removeClass("is-active");
    $("#situational").hide();
    $("#sitTab").removeClass("is-active");
    $("#next").show();
    $("#submit").hide();
}
function showSJ() {
    $("#situational").show();
    $("#sitTab").addClass("is-active");
    $("#numeracy").hide();
    $("#numTab").removeClass("is-active");
    $("#abstract").hide();
    $("#absTab").removeClass("is-active");
    $("#literacy").hide();
    $("#litTab").removeClass("is-active");
    $("#next").hide();
    $("#submit").show();
}

/** Retrieve the id of tab that is active
* Only one tab can be active at a time as the tab
* can only change via the functions on this page
* Use this to determine the next page that should be open
* which button would be relevant to the tab */
function nextOrSubmit() {
    var tabOpen = $( ".is-active" ).attr('id');
    if (tabOpen == "numTab"){
        $("#numeracy").hide();
        $("#numTab").removeClass("is-active");
        $("#literacy").show();
        $("#litTab").addClass("is-active");
        $(document).scrollTop(20);
    } else if (tabOpen == "litTab") {
        $("#literacy").hide();
        $("#litTab").removeClass("is-active");
        $("#abstract").show();
        $("#absTab").addClass("is-active");
        $(document).scrollTop(20);
    }  else if (tabOpen == "absTab") {
        $("#abstract").hide();
        $("#absTab").removeClass("is-active");
        $("#situational").show();
        $("#sitTab").addClass("is-active");
        $("#next").hide();
        $("#submit").show();
        $(document).scrollTop(20);
    }
}
