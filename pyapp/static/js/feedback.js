$('#feedback-form').submit(function (ev) {
    var dataForm = $('#feedback-form').serialize();
    ev.preventDefault();
    $.ajax({
        type: 'POST',
        data: dataForm
    })
    .done(function (response) {
        $('#modal-feedback').modal('show');
        $('#result-feedback').html(response);
        $('#modal-feedback').on('hidden.bs.modal', function () {
            window.location.href = "/"
        });
    })
    .fail(function (error) {
        $('#modal-feedback').modal('show');
        $('#result-feedback').html(error.status + ": " + error.statusText);
    })
});
