var DataRepo = null;
var IntervalStatus = null;

var DataUser = null;
var UserName = "";


/************************************************
**              REPO ANALYSIS
************************************************/

/*
    When a idiom in clicked, show a modal with the idiom information
*/
function showResultModal(idiom) {
    var beautyName = $('#' + idiom + " h3").html();
    $('#result-modal-title').html(beautyName);
    var items_idiom = DataRepo.idioms[idiom];
    $tableBody = $('#table-locations tbody');
    $tableBody.html("");
    if (items_idiom && items_idiom.length > 0) {
        var urlRepo = DataRepo.repository.split(".git")[0] + "/blob/master"
        for (var item in items_idiom) {
            var idiomUrl =  urlRepo + items_idiom[item].file_name + "#L" +
                            items_idiom[item].line;
            var content = "<tr>";
            content += "<td>" + items_idiom[item].file_name + "</td>";
            content += "<td>" + items_idiom[item].line + "</td>";
            content += "<td>" + items_idiom[item].author + "</td>";
            content += "<td><a href='" + idiomUrl + "'>View</a></td>";
            content += "</tr>";
            $tableBody.append(content);
        }
    }
    $('#result-modal').modal();
}

/*
    Is called when the page is loaded only if there are some results
    Show the all the results and call to showAnalysisIdioms
*/
function showResults(data) {
    DataRepo = data;
    console.log(data);
    $('#results').show();
    if (!data){
        alert("No data");
        return
    }
    $(".times").html(0);
    for (item in data.idioms ){
        $("#" + item  + " .times").html(data.idioms[item].length);
    }
    $('.result').click(function () {
        showResultModal($(this)[0].id);
    });
    showAnalysisIdioms();
    var d = new Date(0);
    d.setUTCSeconds(data.lastAnalysis);
    $('#last-analysis').html("Last update: " + d.toLocaleString());
}


/*
    Make and show the analysis of the idioms
*/
function showAnalysisIdioms() {
    var beginner = DataRepo.analysis.beginner;
    var intermediate = DataRepo.analysis.intermediate;
    var advanced = DataRepo.analysis.advanced;
    var beginnerMark = intermediateMark = advanceMark = 0;
    var totalBeginner = totalIntermediate = totalAdvance = 0;
    $('#list-beginner').html('');
    $('#list-intermediate').html('');
    $('#list-advance').html('');
    beginner.forEach(function(idiom){
        totalBeginner++;
        if (idiom.times > 0){
            beginnerMark += 1;
        } else {
            //Show for learn
            $('#list-beginner').append('<a href="' + idiom.info + '" class="list-group-item">' + idiom.beautyName + '</a>')
        }
    });
    intermediate.forEach(function(idiom){
        totalIntermediate++;
        if (idiom.times > 0){
            intermediateMark += 1;
        } else {
            //Show for learn
            $('#list-intermediate').append('<a href="' + idiom.info + '" class="list-group-item">' + idiom.beautyName + '</a>')
        }
    });
    advanced.forEach(function(idiom){
        totalAdvance++;
        if (idiom.times > 0){
            advanceMark += 1;
        } else {
            //Show for learn
            $('#list-advance').append('<a href="' + idiom.info + '" class="list-group-item">' + idiom.beautyName + '</a>')
        }
    });
    //MARK OF EACH LEVEL
    $('#beginner-bar').width(beginnerMark/totalBeginner*100 + '%');
    $('#intermediate-bar').width(intermediateMark/totalIntermediate*100 + '%');
    $('#advance-bar').width(advanceMark/totalAdvance*100 + '%');
    $('#beginner-mark').html(beginnerMark + '/' + totalBeginner);
    $('#intermediate-mark').html(intermediateMark + '/' + totalIntermediate);
    $('#advance-mark').html(advanceMark + '/' + totalAdvance);

    //MESSAGE FOR THE USER
    listLvlObtained = []
    if (beginnerMark/totalBeginner > 0.5) listLvlObtained.push('beginner');
    if (intermediateMark/totalIntermediate > 0.5) listLvlObtained.push('intermediate');
    if (advanceMark/totalAdvance > 0.5) listLvlObtained.push('advanced');

    var msg = ""
    switch (listLvlObtained.length) {
        case 3:
            msg = " and " + listLvlObtained[2];
        case 2:
            msg =  ", " + listLvlObtained[1] + msg;
        case 1:
            msg = "You know a lot about " + listLvlObtained[0] + msg + " pythonic idioms!"
            break
        default:
            msg = "You should improve your pythonic level in all categories";
    }
    msg = "<p>" + msg + "</p>"
    if ((beginnerMark+intermediateMark+advanceMark) < (totalBeginner+totalIntermediate+totalAdvance)){
        msg += "<p>But you can learn a bit more</p>"
    }
    $('#firstMsgResults').html(msg);

    //IDIOMS TO LEARN

}


/*
    Get the status and if is 'Analyzed', reload the page
    otherwise update the bar status and change the text in the button Analyze
*/
function getStatus(url) {
    $.ajax({
        method: 'GET',
        url: '/status/',
        data: {url: url},
        timeout: 2000
    })
    .done(function (data) {
        console.log(data);
        percentage = data.analyzedFiles / data.totalFiles * 100;
        if (data.totalFiles == 0){
            $('#progress-percent').html("0%");
        }else{
            $('#progress-percent').html(Math.round(percentage) + "%");
        }
        $('.analyze-repo-btn').html(data.status);
        $('.analyze-repo-btn').prop('disabled', true);
        $('#progress-bar').width(percentage + "%");
        if (data.status == "Analyzed" || data.status == "Error, try again"){
            if (IntervalStatus) clearInterval(IntervalStatus);
            $('.analyze-repo-btn').html("Analyze again!");
            $('.analyze-repo-btn').prop('disabled', false);
            window.location.reload();
        } else if (data.status == "Repository unavailable") {
            if (IntervalStatus) clearInterval(IntervalStatus);
            $('#progress-bar').parent().hide();
            $('#modal-errors .modal-title').html("Repository unavailable")
            var msg = "<p>This repository is not available in GitHub</p>";
            msg = "<p>Check it out clicking on the url</p>"
            msg += 'If it is available, <a href="/feedback">let us know</a>'
            $('#modal-errors .modal-body').html(msg)
            $('#modal-errors').modal('show');
        }
    })
    .fail(function( jqXHR, textStatus ) {
        console.log( "Request failed status: " + textStatus );
    })
}

/*
    Check the status 1 time.
        If it is anlyzed slide to results
        If is unavailable disable the button analyze
        Otherwise call getStatus with an interval and show the progress bar
*/
function checkstatus() {
    var url = $('#url-project').attr('href');
    $.ajax({
      method: 'GET',
      url: '/status/',
      data: {url: url}
    })
    .done(function (data) {
        console.log(data);
        if (!data.status || data.status == "Analyzed"){
            console.log("status:", data.status);
            $('html, body').animate({
                scrollTop: ($('section.results').offset().top)
            }, 1250, 'easeInOutExpo');
            return
        }
        if (data.status == "Error, try again") {
            console.log("status:", data.status);
            return
        }
        if (data.status == "Repository unavailable"){
            $('.analyze-repo-btn').prop('disabled', true);
            $(".analyze-repo-btn").html(data.status);
            $('#modal-errors .modal-title').html("Repository unavailable")
            var msg = "<p>This repository is not available in GitHub</p>";
            msg = "<p>Check it out clicking on the url</p>"
            msg += 'If it is available, <a href="/feedback">let us know</a>'
            $('#modal-errors .modal-body').html(msg)
            $('#modal-errors').modal('show');
            return
        }
        $('#progress-bar').parent().show();
        $('#progress-percent').html("0%");
        $(".analyze-repo-btn").html("Initializing");
        $('.analyze-repo-btn').prop('disabled', true);
        $('#progress-bar').width("0%");
        if (IntervalStatus) clearInterval(IntervalStatus);
        IntervalStatus = setInterval(function () {
            getStatus(url);
        }, 2000);
    })
    .fail(function( jqXHR, textStatus ) {
      console.log( "Request failed status: " + textStatus );
  });
}

/*
    Is called when the button analyze is pressed and make a POST to analyze the
    repository. On success, reload the web
*/
function analyzeRepository(url, onlymodified) {
    $('.analyze-repo-btn')
    .text('Analyzing...')
    .append('<i class="fa fa-spinner fa-pulse fa-fw loading-circle"></i>')
    .prop('disabled', true);
    onlymodified = onlymodified ? 1 : 0;
    $.ajax({
      method: 'POST',
      url: '/analyze-repo/',
      data: {url: url, onlymodified:onlymodified}
    })
    .done(function (reply) {
        window.location.href = reply.redirect;
    })
    .fail(function( error ) {
        $('#modal-errors .modal-title').html("Error")
        var msg = "<p>" + error.status + ": " + error.statusText + "</p>";
        var msg = "<p>" + error.responseText + "</p>"
        msg += '<a href="/feedback">Our mistake? Tell us</a>';
        $('#modal-errors .modal-body').html(msg);
        $('#modal-errors').modal('show');

        $('.analyze-repo-btn')
        .text('Analyze it!')
        .prop('disabled', false);

    });
}

/*
    index.html
    Call to analyzeRepository with the url specified
*/

$('#analyze-repo-form').on('submit', function (ev) {
  ev.preventDefault();
  DataRepo = null;
  var url = $('#url-project').val();
  if ( !validUrlGH(url) ){
      showUrlFormatModal();
      return
  }
  var onlyModifiedFiles = $('#only-modified-check').prop('checked');
  analyzeRepository(url, onlyModifiedFiles);
});
/*
    results-repo.html
    Call to analyzeRepository with the url specified
*/
$('#analyze-this-repo').click(function () {
    var url = $('#url-project').attr('href');
    var onlyModifiedFiles = $('#only-modified-check').prop('checked');
    analyzeRepository(url, onlyModifiedFiles);
});


/*************************************************
**                USER ANALYSIS
**************************************************/

function showUserRepos(userdata) {
    DataUser = userdata
    console.log(userdata);
    if (!userdata){
        alert("No data")
        return
    }
    $('#user-repos').show();
    $('html, body').animate({
        scrollTop: ($('#user-repos').offset().top - 50)
    }, 1250, 'easeInOutExpo');

    $tableBody = $('#table-repos-user tbody');
    $tableBody.html("");

    DataUser.forEach(function (repo) {
        var content = "<tr>";
        if (repo.language == "Python") {
            content += '<td><input type="checkbox" checked></td>';
        } else {
            content += '<td><input type="checkbox"></td>';
        }
        content += "<td>" + repo.name + "</td>"
        if (repo.fork){
            content += '<td><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></td>';
        } else {
            content += '<td></td>';
        }
        content += "<td>" + repo.language + "</td>"
        content += "<td><a href='" + repo.html_url + "'>View</a></td>"
        content += "</tr>";
        $tableBody.append(content);
    });
}


function getUserRepos(user) {
    $('#repos-user-btn')
    .text('Getting repositories...')
    .append('<i class="fa fa-spinner fa-pulse fa-fw loading-circle"></i>')
    .prop('disabled', true);

    $.ajax({
      method: 'GET',
      url: '/repos-user/',
      data: {'username-gh': user}
    })
    .done(showUserRepos)
    .fail(function(error ) {
        $('#modal-errors .modal-title').html("Check your username again")
        var msg = "<p>" + error.status + ": " + error.statusText + "</p>";
        msg += '<a href="/feedback">Tell us if it wasn\'t your mistake </a>and provide the entered username'
        $('#modal-errors .modal-body').html(msg)
        $('#modal-errors').modal('show');
        console.log(error);
    })
    .always (function(){
      $('#repos-user-btn').text('Analyze my repositories!')
      .prop('disabled', false);
    })

}

$('#repos-user-form').on('submit', function (ev) {
  ev.preventDefault();
  DataRepo = null;
  var username = $('#username-gh').val();
  UserName = username;
  if (!username) {
      alert("Username not intruduced");
      return
  }
  getUserRepos(username);
});


$('#add-project-contrib').click(function(ev) {
    ev.preventDefault();
    var url = $('#url-project-contrib').val();
    if ( !validUrlGH(url) ) {
        showUrlFormatModal();
        return
    }
    var r = /https\:\/\/github\.com\/(.+\/.+)\.git$/
    match = url.match(r)
    var content = "<tr>";
    content += '<td><input type="checkbox" checked></td>';
    content += "<td>" + match[1] + "</td>"
    content += "<td> -- </td>"
    content += "<td> -- </td>"
    content += "<td><a href='https://github.com/" + match[1] + ".git'>View</a></td>"
    content += "</tr>";
    $('#table-repos-user tbody').append(content);
});


function analyzeUserRepos(reposList, user) {
    var data = {'repos': JSON.stringify(reposList), 'username': user}
    $.ajax({
      method: 'POST',
      url: '/analyze-repos-user/',
      data: data
    })
    .done(function (reply) {
        window.location.href = reply.redirect;
    })
    .fail(function( error ) {
        $('#modal-errors .modal-title').html("Error")
        var msg = "<p>" + error.status + ": " + error.statusText + "</p>";
        msg += '<p>' + error.responseText + '</p>'
        msg += '<a href="/feedback">Our mistake? Tell us</a>';
        $('#modal-errors .modal-body').html(msg);
        $('#modal-errors').modal('show');
        console.log(error);
    })
    .always (function(){
        $('#analyze-repos-user-btn').text('Analyze the selected repositories!')
        .prop('disabled', false);
    })
}

$('#analyze-repos-user-btn').click(function (ev) {
    $('#analyze-repos-user-btn').text('Wait a second...')
    .append('<i class="fa fa-spinner fa-pulse fa-fw loading-circle"></i>')
    .prop('disabled', true);
    ev.preventDefault();
    $tableBody = $('#table-repos-user tbody');
    var repositories = [];
    $tableBody.children().each(function(i, item) {
         if (item.childNodes[0].firstChild.checked) {
             console.log(item.childNodes[0].firstChild.checked);
             var repoName = item.childNodes[1].firstChild.data;
             repositories.push("https://github.com/" + repoName + ".git");
         }
    });
    //var emailNotif = $('#email-notify').val();
    analyzeUserRepos(repositories, UserName);
});


function showUrlFormatModal() {
    $('#modal-errors .modal-title').html("Bad URL");
    var msg = "<p>Your url doesn't fit the format:</p>";
    msg = "<p>Format: https://github.com/USERNAME/REPOSITORY.git</p>"
    msg += "<p>Remain it should be <strong>https</strong> and ends with <strong>.git</strong></p>"
    msg += '<a href="/feedback">Our mistake? PLEASE, copy and send us your url</a>'
    $('#modal-errors .modal-body').html(msg)
    $('#modal-errors').modal('show');
}

function validUrlGH(url) {
    var r = /^https\:\/\/github\.com\/.+\/.+\.git$/
    var match = url.match(r)
    if (!match) {
        return false
    }
    var spl = url.split('/')
    if (spl.length != 5){
        return false
    }
    return true
}
