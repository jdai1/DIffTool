$(document).ready( function() {
	$('#fileManager').click( function() {
		$.ajax({
	        url:'/FileManager/',
	        type: 'GET',
	        headers:{'authorization':window.sessionStorage.getItem("token")}
    	});
	})

	$('#diffTool').click( function() {
		$.ajax({
	        url:'/DiffTool/',
	        type: 'GET',
	        headers:{'authorization':window.sessionStorage.getItem("token")}
    	});
	})

	$('#status').click( function() {
		$.ajax({
	        url:'/Status/',
	        type: 'GET',
	        headers:{'authorization':window.sessionStorage.getItem("token")}
    	});
	})

	$('#logout').click( function() {
		alert('session token revoked');
	});
});