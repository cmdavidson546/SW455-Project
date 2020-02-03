$(document).ready(function() {
    $('form').on('submit', function(event) {
        event.preventDefault();

        // the ajax call will send the email and password info to app.py for processing
        $.ajax({
            data: {
                email: $('#email').val(),
                password: $('#password').val()
            },
            type: 'POST',

            url: '/auth/js/process_login'  // or.. https://sweng-455-project.herokuapp.com/process_login

            //url: 'https://sweng-455-project.herokuapp.com/static/js/process_login'
        })
        // the call back from app.py will send an alert to the user if entered info is not valid
        // else we create a hidden <form> and pass the data via POST to the new endpoint using form.submit()
        .done(function(data) {
            if(data.error) {
                alert(data.error);
            }
            else {
                 // This uses GET ... which is not what we want
                //window.location = '/auth/login/'+data.email+'/'+data.password;
                var url = '/auth/login';
                var form = $('<form style="display:none;" action="' + url + '" method="post" >' + '<input type="text" name="email" value="' + data.email + '" />' + '<input type="password" name="password" value="' + data.password + '" />' + '</form>');
                $('body').append(form);
                form.submit();

            }
        })
    });
});
