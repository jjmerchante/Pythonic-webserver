/*
    POST the server the repositories and username and begin to scan them
    This will reload the web page
*/
function analyzeUserRepos(repositories, username) {
    var data = {'repos': JSON.stringify(repositories), 'username': username}
    $('.analyze-user-btn')
    .text('Analyzing...')
    .append('<i class="fa fa-spinner fa-pulse fa-fw loading-circle"></i>')
    .prop('disabled', true);
    //onlymodified = onlymodified ? 1 : 0;
    $.ajax({
      method: 'POST',
      url: '/analyze-repos-user/',
      data: data
    })
    .done(function (reply) {
        window.location.href = reply.redirect;
    })
    .fail(function( jqXHR, textStatus ) {
      alert( "Request failed: " + textStatus );
    })
    .always(function () {
        $('.analyze-user-btn')
        .text('Analyze!')
        .prop('disabled', false);
    });
}

/*
    Analyze the repositories in the table
*/
$('#analyze-this-user').click(function (ev) {
    ev.preventDefault();
    $tableBody = $('#table-repos-user tbody');
    var repositories = [];
    $tableBody.children().each(function(i, item) {
         if (item.childNodes[0].firstChild.checked) {
             //console.log(item.childNodes[0].firstChild.checked);
             var repoName = item.childNodes[1].firstChild.data;
             repositories.push("https://github.com/" + repoName + ".git");
         }
    });
    var username = location.pathname.split('/')[2];
    //var emailNotif = $('#email-notify').val();
    analyzeUserRepos(repositories, username);
});


/*
    For adding a URL to the user repositories
*/
$('#add-project-contrib').click(function(ev) {
    ev.preventDefault();
    var url = $('#url-project-contrib').val();
    var r = /https\:\/\/github\.com\/(.+\/.+)\.git/
    var match = url.match(r)
    if (!match || match.length < 2) {
      alert("Check the url again")
      return
    }
    var content = '<tr>'
    content += '<td>' + url + '</td>'
    content += '<td><a href="' + url + '">Link</a></td>'
    content += '<td> -- </td>'
    content += '<td> -- </td>'
    content += '<td>TODO</td>'
    $('#table-repos-user tbody').append(content);
    $('#url-project-contrib').val('');
});


/*
    Check the status 1 time.
        If it is analyzed do nothing
        If is unavailable disable the button analyze
        Otherwise call getStatus with an interval and show the progress bar
        AND SCROLL TO ANALYSIS SECTION
*/
function checkstatus(url, target) {
    $.ajax({
      method: 'GET',
      url: '/status/',
      data: {url: url}
    })
    .done(function (data) {
        console.log(data);
        if (!data.status || data.status == "Analyzed" || data.status == "Error, try again"){
            $('html, body').animate({
                scrollTop: 0
            }, 1250, 'easeInOutExpo');
            return
        }
        if (data.status == "Repository unavailable"){
            return
        }
        $(target.cells[4]).children().addClass('gly-spin')
        $(target.cells[4]).prop('disabled', true);

        var intervalStatus = setInterval(function () {
            getStatus(url, intervalStatus, target);
        }, 5000);
        $('#notify-box').show();

    })
    .fail(function( jqXHR, textStatus ) {
      console.log( "Request failed status: " + textStatus );
  });
}

/*
    Get the status and if is 'Analyzed', reload the page
    otherwise update the status
*/
function getStatus(url, interval, target) {
    $('html, body').animate({
        scrollTop: ($('section#analyze-section').offset().top)
    }, 1250, 'easeInOutExpo');

    $.ajax({
        method: 'GET',
        url: '/status/',
        data: {url: url},
        timeout: 2000
    })
    .done(function (data) {
        percentage = data.analyzedFiles / data.totalFiles * 100;
        if (data.totalFiles == 0){
            $(target).children('.table-repo-status').html(data.status + " - 0%");
        }else{
            $(target).children('.table-repo-status').html(data.status + " - " + Math.round(percentage) + "%");
        }

        if (data.status == "Analyzed" || data.status == "Repository unavailable" || data.status == "Error, try again"){
            if (interval) clearInterval(interval);
            $(target).children(".glyphicon-refresh").removeClass('gly-spin');
            $(target).children("button").prop('disabled', false);
            window.location.reload();
        }

    })
    .fail(function( jqXHR, textStatus ) {
        console.log( "Request failed status: " + textStatus );
    });
}

$('.update-repository-table').click(function (ev) {
    $(ev.target).children().addClass('gly-spin');
    $(ev.target).prop('disabled', true);
    var targetParent = ev.target.parentElement.parentElement;
    console.log(targetParent);
    analyzeRepository("https://github.com/" + targetParent.id + ".git", targetParent)
});

/*
    Is called when the button analyze is pressed
    POST /analyze-repo/ to analyze the repository. On success, reload the web
*/
function analyzeRepository(url, target) {
    //TODO: Onlymodified
    $.ajax({
      method: 'POST',
      url: '/analyze-repo/',
      data: {url: url, onlymodified:0}
    })
    .fail(function( jqXHR, textStatus ) {
        alert( "Request failed: " + textStatus );
    })
    .always(function() {
        $(target).children().removeClass('gly-spin');
        $(target).children("button").prop('disabled', false);
    });
    var intervalStatus = setInterval(function () {
        getStatus(url, intervalStatus, target);
    }, 2000);
}

function getStatusReposUser() {
    var ch = $("#table-repos-user tbody").children()
    console.log(ch);
    for (var i = 0; i< ch.length; i++){
        var proj = ch[i];
        checkstatus(proj.cells[0].innerHTML, proj)
    }
}


$('#notification-form').submit(function (ev) {
    var dataForm = $('#notification-form').serialize();//path and email
    console.log(dataForm);
    $('#notify-box button.close').collapse('hide');
    $('#email-notify').val('');
    ev.preventDefault();
    $.ajax({
      method: 'POST',
      url: '/notificate',
      data: dataForm
    })
    .fail(function( error ) {
        alert(error.text);
    })
    .done(function(data) {
        alert(data);
    });
});

/*****************************************************************************/
$('#open-add-repo').click(function () {
    $('#repositories-modal').modal();
});
