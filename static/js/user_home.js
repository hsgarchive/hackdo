$(document).ready(function(){

    //To start datepicker
    $('.datepicker').datetimepicker({
        pickTime: false
    });

    var csrftoken = $.cookie('csrftoken');
    /*
     * Builds AJAX URL
     */
    var _buildURL = function(review_id) {
        var url = window.location.pathname;

        return url.substring( 0, url.indexOf( 'users' ) ) + 'review_membership/' + review_id + '/';
    };

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $('.review').each(function() {
        var thisCheck = $(this);
        var container = thisCheck.parent().parent().parent();
        var tr = container.parent();
        thisCheck.click (function(){
            if ( thisCheck.is(':checked') ) {
                $.ajax({
                    type: 'POST',
                    crossDomain: false,
                    url: _buildURL(thisCheck.val()),
                    beforeSend:function(xhr, settings){
                        // add csrf header and set loading image
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        container.html('<img src="/static/img/loading.gif" alt="Loading..." />');
                    },
                    success:function(data){
                        if (data.success) {
                            // review done; give feedback to user
                            container.html('<span class="label label-success">Reivewed</span>');
                            tr.removeClass("warning");
                            tr.addClass("success");
                        }
                        else {
                            // review error; give feedback to user
                            container.html('<span class="label label-important"><strong>Error!</strong> '+data.errors.message+'</span>');
                        }
                    },
                    error:function(){
                        // failed request; give feedback to user
                        container.html('<span class="label label-important"><strong>Oops!</strong> Can\'t make ajax request.</span>');
                    }
                });
            }
        });
    });

});
