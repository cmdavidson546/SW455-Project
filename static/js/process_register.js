$(document).ready(function() {
    $('form').on('submit', function(event) {
        event.preventDefault();

        // the ajax call will send the email and password info to app.py for processing
        $.ajax({
            data: {
                name: $('#name').val(),
                email: $('#email').val(),
                password: $('#password').val()
            },
            type: 'POST',
            url: '/process_register'
        })
        // the call back from app.py will send an alert to the user if entered info is not valid
        // else we create a hidden <form> and pass the data via POST to the new endpoint using form.submit()
        .done(function(data) {
            if(data.error) {
                alert(data.error);
            }
            else {
                var url = '/auth/register';
                var form = $('<form style="display:none;" action="' + url + '" method="post" >' +
                '<input type="text" name="name" value="' + data.name + '" />' +
                '<input type="text" name="email" value="' + data.email + '" />' +
                '<input type="password" name="password" value="' + data.password + '" />' +
                '</form>');

                $('body').append(form);
                form.submit();
            }
        })
    });
});