// grab json data and initialize bootstrap-treeview
var obj = JSON.parse(document.currentScript.getAttribute('data'));
var treeSelector = $('#tree');
treeSelector.treeview({
    color: "#4a8cc8",
    data: obj,
    onNodeSelected: function(event, data) {
        /* for expand / collapse on click:
        if (data.state.expanded == false) {
            treeSelector.treeview('expandNode', [data.nodeId, {levels: 1, silent: true}]);
        }
        else {
            treeSelector.treeview('collapseNode', [data.nodeId, {levels: 1, silent: true}]);
        }
        */
        nodeSelection(event, data);
    }
});
treeSelector.treeview('expandAll', { levels: 1, silent: true });

function expand_nodes(data, to_expand) {
    $.ajax({
        url:'expand_nodes',
        type: 'GET',
        data:{'data':JSON.stringify(data), 'expand':JSON.stringify(to_expand)}, 
        headers:{'authorization':window.sessionStorage.getItem("token")},
        success: function(returnedData) {
            $.each(JSON.parse(returnedData), function(index, value) {
                treeSelector.treeview('expandNode', [ value.nodeId, { levels: 1, silent: true } ])
            });
        }
    });
}

// update tree when file is deleted
$(document).ready( function() {
    // add authorization headers
    $('#fileupload').bind('fileuploaddestroy', function (e, data) {
            data.headers = {'authorization':window.sessionStorage.getItem("token")};
            console.log('header added');
    });
    $('#fileupload').bind('fileuploadadd', function (e, data) {
        data.headers = {'authorization':window.sessionStorage.getItem("token")};
        console.log('header added');
    });
    // update treeview on add and delete
    $('#fileupload').on('fileuploaddone', function(e, data) {
        $.ajax({
            url:'update_treeview',
            type: 'GET',
            data:{'type':'view'},
            headers:{'authorization':window.sessionStorage.getItem("token")},
            success: function(returnedData) {
                    var expanded_nodes = [];
                    $.each(treeSelector.treeview('getExpanded'), function(index, value) {
                       expanded_nodes.push(value['tags'][0]);
                    });
                    treeSelector.treeview({
                        color: "#4a8cc8",
                        data: JSON.parse(returnedData),
                        onNodeSelected: function(event, data) {
                            nodeSelection(event, data);
                        }
                    });
                    expand_nodes(treeSelector.treeview('getUnselected'), expanded_nodes);
            }
        });
    });
    $('#fileupload').on('fileuploaddestroyed', function(e, data) {
        $.ajax({
            url:'update_treeview',
            type: 'GET',
            data:{'type':'view'},
            headers:{'authorization':window.sessionStorage.getItem("token")},
            success: function(returnedData) {
                    var expanded_nodes = [];
                    $.each(treeSelector.treeview('getExpanded'), function(index, value) {
                        expanded_nodes.push(value['tags'][0]);
                    });
                    treeSelector.treeview('remove');
                    treeSelector.treeview({
                        color: "#4a8cc8",
                        data: returnedData,
                        onNodeSelected: function(event, data) {
                            nodeSelection(event, data);
                        }
                    });
                    expand_nodes(treeSelector.treeview('getUnselected'), expanded_nodes);
            }
        });
    });
});

function nodeSelection(event, data) {
    var tag = data['tags'][0];
    var name = data['text'];
    var seg = tag.split('/');
    var url = "";
    for (var i = 1; i < seg.length; i++) {
        if (i < seg.length - 1) {
            url = url + seg[i] + '|';
        }
        else {
            url += seg[i];
        }
    }
    if (name.localeCompare('wip') == 0 || name.localeCompare('stock') == 0) {
        //document.write('selected');
        $("#tbody").empty();
        uploadSelector = $('#fileupload');
        uploadSelector.fileupload({
            // Uncomment the following to send cross-domain cookies:
            //xhrFields: {withCredentials: true},
            url: 'upload/' + url
        });
        $.ajax({
            // Uncomment the following to send cross-domain cookies:
            //xhrFields: {withCredentials: true},
            url: uploadSelector.fileupload('option', 'url'),
            type: 'GET',
            dataType: 'json',
            headers: {'authorization':window.sessionStorage.getItem("token")},
            context: uploadSelector[0]
        }).always(function () {
            $(this).removeClass('fileupload-processing');
        }).done(function (result) {
            $(this).fileupload('option', 'done')
                .call(this, $.Event('done'), {result: result});
        });
    }
}

$(document).ready( function() {
    $("#add_directory").click( function() {
        var value = $('#dirname').val();
        if (value == '') {
            alert('Invalid Directory Name')
        }
        else {
            $.ajax({
                url:'/FileManager/action_folder/' + value,
                type: 'GET',
                data: {'action': 'add'},
                headers:{'authorization':window.sessionStorage.getItem("token")},
                success: function (returnedData) {
                    var expanded_nodes = [];
                    $.each(treeSelector.treeview('getExpanded'), function(index, value) {
                        expanded_nodes.push(value['tags'][0]);
                    });
                    //treeSelector.empty();
                    treeSelector.treeview({
                        color: "#4a8cc8",
                        data: returnedData,
                        onNodeSelected: function(event, data) {
                            nodeSelection(event, data);
                        }
                    });
                    expand_nodes(treeSelector.treeview('getUnselected'), expanded_nodes);
                }
            });
        }
    });
    $("#delete_directory").click( function() {
        var checked = treeSelector.treeview('getSelected');
        if (checked[0]['tags'][1] == 'delete') {

            $.ajax({
                url: '/FileManager/action_folder' + checked[0]['tags'][0],
                type: 'GET',
                data: {'action': 'delete'},
                headers: {'authorization': window.sessionStorage.getItem("token")},
                success: function (returnedData) {
                    var expanded_nodes = [];
                    $.each(treeSelector.treeview('getExpanded'), function (index, value) {
                        expanded_nodes.push(value['tags'][0]);
                    });
                    //treeSelector.empty();
                    treeSelector.treeview({
                        color: "#4a8cc8",
                        data: returnedData,
                        onNodeSelected: function (event, data) {
                            nodeSelection(event, data);
                        }
                    });
                    expand_nodes(treeSelector.treeview('getUnselected'), expanded_nodes);
                }
            });
        }
        else {
            alert('Invalid directory');
        }
    });
});