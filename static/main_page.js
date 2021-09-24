$(document).ready(function() {

    reloadTaskList();
    function getTotalTaskCount() {
        var sum = 0;
        $('.task_category_count').each(function(){
            sum += parseInt($(this).text());  
        });
        
        $('#total_task_count').text("(" + sum + ")");

        $('.date-block-header').each(function() {
    
            let block_header = $(this);
            let k = block_header.attr('date-block');
            let block_items = $('ol[date-block='+k+']');

        
            item_count = block_items.children().length ;
            if(item_count == 0) {
                block_header.remove();
                block_items.remove();
            }
        });

    }

    function reloadTaskList() {
        console.log(' reloading task list');
        category_id = $('#filter_category_id').val();
        message_box = $('#message');
        $.ajax({
            url: '/ajax/main_task_list',
            data: {
                'category_id': category_id
            },
            dataType: 'html',
            success: function(data) {
                if (data) {
                    $('#task_list').html(data);
                    getTotalTaskCount();
                    addCallbacks();

                } else {
                    console.log("Error has occured during request" + (data?": " + data:""));
                    message_box.text('Error has occured during request' + (data?": " + data:""));
                    message_box.fadeIn('slow', function() {
                        message_box.delay(5000).fadeOut();
                    });

                }

            }
        });

    }
    
    function addCallbacks() {

	    $(".link_task_done").on( "click", function() {
		task_id = $(this).attr('task-id')
		console.log(' marking as done  task_id ' + task_id);

		message_box = $('#message');
		$.ajax({
		    url: '/ajax/task/done',
		    data: {
			'task_id': task_id
		    },
		    dataType: 'json',
		    success: function(data) {
			if (data.result) {
			    console.log("Result:" + data.result);
			    reloadTaskList();


			} else {
			    console.log("Error has occured during request" + (data.error?": " + data.error:""));
			    message_box.text('Error has occured during request' + (data.error?": " + data.error:""));
        			message_box.fadeIn('slow', function() {
	        		    message_box.delay(5000).fadeOut();
		        	});

			}

		    }
		});
		return false;
	    });

	    $(".link_task_postpone").click(function() {
		task_id = $(this).attr('task-id');
		delay_shift = $(this).attr('delay-shift');
		console.log(' delaying task_id ' + task_id + ' for ' + delay_shift + ' days');
		message_box = $('#message');
		$.ajax({
		    url: '/ajax/task/postpone',
		    data: {
			'task_id': task_id,
			'delay_shift': delay_shift
		    },
		    dataType: 'json',
		    success: function(data) {
			if (data.result) {

			    console.log("Result:" + data.result);
			    reloadTaskList();

			} else {
			    console.log("Error has occured during request" + (data.error?": " + data.error:""));
			    message_box.text('Error has occured during request' + (data.error?": " + data.error:""));
        			message_box.fadeIn('slow', function() {
	        		    message_box.delay(5000).fadeOut();
		        	});

			}

		    }
		});
		return false;
	    });

    }
});    
