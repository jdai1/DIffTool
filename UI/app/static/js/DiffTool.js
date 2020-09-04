// grab json data and initialize bootstrap-treeview
var obj = JSON.parse(document.currentScript.getAttribute('data'));
var treeSelector = $('#tree');
treeSelector.treeview({
    color: "#4a8cc8",
    data: obj,
    multiSelect: true
});
treeSelector.treeview('expandAll', {levels: 1, silent: true});

function expand_nodes(data, to_expand) {
    $.ajax({
        url: '/DiffTool/expand_nodes',
        type: 'GET',
        data: {'data': JSON.stringify(data), 'expand': JSON.stringify(to_expand)},
        headers: {'authorization': window.sessionStorage.getItem("token")},
        success: function (returnedData) {
            $.each(JSON.parse(returnedData), function (index, value) {
                treeSelector.treeview('expandNode', [value.nodeId, {levels: 1, silent: true}])
            });
        }
    });
}

$(document).ready( function() {
    $("#compare").click( function() {
        var selectedNodes = treeSelector.treeview('getSelected');
        var displaySelector = $('#display');
        displaySelector.empty();
        if (Object.keys(selectedNodes).length > 2) {
            displaySelector.append('<div class="alert alert-danger"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>Only 2 folders can be selected at a time</div>');
        }
        else if (Object.keys(selectedNodes).length < 2) {
            displaySelector.append('<div class="alert alert-danger"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>Please select 2 folders.</div>');
        }
        else {
            // assign and valdiate folders
            if (selectedNodes[0]['text'] == 'wip' && selectedNodes[1]['text'] == 'stock') {
                var wip = selectedNodes[0];
                var stock = selectedNodes[1];
            }
            else if (selectedNodes[0]['text'] == 'stock' && selectedNodes[1]['text'] == 'wip') {
                var wip = selectedNodes[1];
                var stock = selectedNodes[0];
            }
            else {
                displaySelector.append('<div class="alert alert-danger"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>Incompatible folders.</div>');
            }
            var wip_path = wip['tags'][0];
            var stock_path = stock['tags'][0];
            $.ajax({
                url: '/DiffTool/compare',
                type: 'GET',
                data: {'wip_path': wip_path, 'stock_path': stock_path},
                headers: {'authorization': window.sessionStorage.getItem("token")},
                success: function (returnedData) {
                    if (returnedData == 'ERROR') {
                        displaySelector.append('<div class="alert alert-danger"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>Invalid system. Linux not allowed.</div>');
                    } else if (returnedData == 'TIME') {
                        displaySelector.append('<div class="alert alert-danger"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>Incorrect chronological order</div>')
                    } else {
                        $.ajax({
                            url: '/DiffTool/update_treeview',
                            type: 'GET',
                            data: {'type': 'tool'},
                            headers: {'authorization': window.sessionStorage.getItem("token")},
                            success: function (returnedData) {
                                var expanded_nodes = [];
                                $.each(treeSelector.treeview('getExpanded'), function (index, value) {
                                    expanded_nodes.push(value['tags'][0]);
                                });
                                treeSelector.treeview({
                                    color: "#4a8cc8",
                                    data: JSON.parse(returnedData),
                                    multiSelect: true
                                });
                                expand_nodes(treeSelector.treeview('getUnselected'), expanded_nodes);
                            }
                        });
                        displaySelector.append('<div class="alert alert-success"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>Files successfully compared</div>')
                    }
                }
            });
        }
    });
});