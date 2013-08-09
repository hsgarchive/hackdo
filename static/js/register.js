$(document).ready(function(){
    var name_list = $('#id_refer_one').data('source');
    $('#id_username').blur(function() {
        var input = $(this);
        var user_typed = input.val();
        var span = input.parent().find('.help-inline');
        var control_group = input.parent().parent();
        if (user_typed !== "" && $.inArray(user_typed, name_list)>-1) {
            control_group.addClass("error");
            span.html('<ul class="errorlist"><li>Username is already taken.</li></ul>');
        }
        else {
            control_group.removeClass("error");
            span.empty();
        }
    });
});
