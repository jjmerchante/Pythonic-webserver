/***************SOME INITIALIZATION FOR CSRFTOKEN*********************/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
/******************************END*********************************/
/*
    Code for alpha version feedback
*/
$(".feedback-alert").click(function () {
    window.location = "/feedback"
});

/*
    Code for minimizate and maximizate window
*/
$('#notify-box button').on('click', function (e) {
    var $this = $(this.children[0]);
    console.log($this.hasClass('glyphicon-minus'));
    if ($this.hasClass('glyphicon-minus')) {
        $this.removeClass('glyphicon-minus').addClass('glyphicon-plus');
    } else {
        $this.removeClass('glyphicon-plus').addClass('glyphicon-minus');
    }
});

/*
    Code for search results of users or repositories
*/
document.addEventListener("DOMContentLoaded", function(event) {
    $('#repo-form-search').submit(function(ev) {
        ev.preventDefault();
        var repo = $('#name-repo').val();
        var user = $('#name-user-repo').val();
        if (repo != "" && user != "") {
            window.location.href = "/repository/" + user + "/" + repo
        }
        $('#name-repo').val('')
        $('#name-user-repo').val('')
    });
    $('#user-form-search').submit(function(ev) {
        ev.preventDefault();
        var user = $('#name-user').val();
        if (user != "") {
            window.location.href = "/user/" + user
        }
        $('#name-user').val('');
    });
});
