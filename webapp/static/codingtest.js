
$(document).ready(function(){
    var str = ` class Solution:
    def permute(self, nums):
        """
        :type nums: List[int]
        :rtype: List[List[int]]
        """
        for i in range(math.factorial(nums)):
            print(i) 
    `
    var code = $(".codemirror-textarea")[0];
    var editor = CodeMirror.fromTextArea(code, {
        lineNumbers : true,
        mode : "python"
    });
    // $(".ss").click(function(){
    //     $(".ss").addClass("is-loading");
    // });


    $("#codeForm").submit(function(e) {
        var form = $('#codes');
        var url = form.attr('action');
    
        $.ajax({
               type: "POST",
               
               data: form.serialize(), // serializes the form's elements.
               success: function(data)
               {
                $("#submitResponseBox").css("font-family", "Monospace");
                $("#submit").click(function() {
                   $("#submitResponseBox").text("Your code has been submitted, thank you."); // show response from the php script.
                }
                )
                $("#run").click(function() {
                    $("#submitResponseBox").text("Your code has been , thank you."); // show response from the php script.
                 }
                 )

                }
               
             });
    
        e.preventDefault(); // avoid to execute the actual submit of the form.
    });

});

