$(document).ready( function() {

    $('#login').submit( function(e) {
        e.preventDefault();
        $.ajax({
            url: '/User/login',
            data: $(this).serialize(),
            type: 'POST',
            success: function(data) {
                if (data == 'Error') {
                    location.reload();
                }
                else {
                    window.sessionStorage.setItem("token", data);
                    alert('session token added');
                    $.ajax({
                        url:'/User/redirect',
                        type: 'GET',
                        headers:{'authorization':window.sessionStorage.getItem("token")},
                        success: function(returnedData) {
                            window.location = returnedData;
                        }
                    });
                }
            }
        });
    });
});