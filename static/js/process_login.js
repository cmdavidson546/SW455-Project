$(document).ready(function() {
    $('#login-form').on('submit', function(event) {
        event.preventDefault();

        $.ajax({
            data: {
                email: $('#email').val(),
                password: $('#password').val()
            },
            type: 'POST',

            url: '/auth/process_login'  

        })
        .done(function(data) {
            if(data.error) {
                alert(data.error);
            }
            else {
                var url = '/auth/login';
                var form = $('<form style="display:none;" action="' + url + '" method="post" >' + '<input type="text" name="email" value="' + data.email + '" />' + '<input type="password" name="password" value="' + data.password + '" />' + '</form>');
                $('body').append(form);
                form.submit();

            }
        })
    });
});
