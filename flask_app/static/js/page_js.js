
$(document).ready(function() {
    update_data();
   
});


function update_data() {
    
    console.log("Updating_data");
    $.ajax({
        url : 'get_data',
        type : 'GET',
        success: function(data) {
            render_data(JSON.parse(data));
        },
        error: function(request,error) { console.log(error); }
    });
    
}


function render_data(data) {
    console.log('here');
    console.log(data['data'].length)
    console.log(data['data'])

    // Declare datatable object
    var dataTable = $('#mainTable').DataTable({
        'paging': false,
        'order': [[3, 'desc']],
        'searching': false,
        'columnDefs': [
            {
                'render': function (data, type, row) {
                    return '<a href="https://prices.runescape.wiki/osrs/item/' + row[5] + '" target="_blank">' + data + '</a>';
                },
                'targets': 0
            },
            
        ]
    });

    // Iterate over data returned from API and populate rows in the datatable
    for (var i=0; i < data['data'].length; i++) {
        var ele = data['data'][i];

        // display the highest value of each data field
        if (ele['high_min_max_diff_int'] > ele['low_min_max_diff_int']) {
            var min_max_margin = ele['high_min_max_diff_int'];
        } else {
            var min_max_margin = ele['low_min_max_diff_int'];
        }

        if (ele['high_min_max_diff_percent'] > ele['low_min_max_diff_percent']) {
            var min_max_diff = ele['high_min_max_diff_percent'];
        } else {
            var min_max_diff = ele['low_min_max_diff_percent'];
        }

        if (ele['high_recent_to_max_diff'] > ele['low_recent_to_max_diff']) {
            var recent_diff = ele['high_recent_to_max_diff'];
        } else {
            var recent_diff = ele['low_recent_to_max_diff'];
        }
        
        if (ele['high_volume_avg'] > ele['low_volume_avg']) {
            var volume = ele['high_volume_avg'];
        } else {
            var volume = ele['low_volume_avg'];
        }

        dataTable.row.add([
            ele['name'],
            min_max_margin,
            min_max_diff + '%',
            recent_diff + '%',
            volume,
            ele['id']
        ]).draw(false);

    }

    // Update the time
    var timestamp = data['data'][0]['timestamp'];
    $('#updateTime').html(generateDateTime(timestamp));
}


function generateDateTime(timestamp) {
    var dateObj = new Date(timestamp * 1000);
    var date = dateObj.toLocaleDateString('en-US');
    var time = dateObj.toLocaleTimeString("en-US");

    return date + ' ' + time;
}




