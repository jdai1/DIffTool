var events = JSON.parse(document.currentScript.getAttribute('data'));
for (var key in events) {
    document.getElementById('log').value += events[key];
    document.getElementById('log').value += '\n';
}
$(document).ready( function() {
    $('#clear').click( function() {
        document.getElementById('log').value = '';
        $.ajax({
            url:'/Status/clear_events',
            type: 'GET',
            headers: {'authorization': window.sessionStorage.getItem("token")}
        })
    });
});