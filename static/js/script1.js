$(document).ready(function() {
    var max_fields = 10;
    var wrapper = $(".container1");
    var add_button = $(".add_form_field");
  
    var x = 3;
    $(add_button).click(function(e) {
        e.preventDefault();
        if (x < max_fields) {
            x++;
            $(wrapper).append('<div class="input-field col s4"><label for="s'+x+'"><b>Disease-'+x+'</b></label><br><input id="s'+x+'" name="Disease'+x+'" placeholder="Diseases'+x+'" type="text" class="validate"><a href="#" class="delete">Delete</a></div>'); //add input box
        } else {
            alert('You Reached the limits')
        }
    });
  
    $(wrapper).on("click", ".delete", function(e) {
        e.preventDefault();
        $(this).parent('div').remove();
        x--;
    })
  });