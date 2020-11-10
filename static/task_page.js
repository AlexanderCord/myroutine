$(document).ready(function() {
    function refreshHistory(task_id) {
        $.ajax({
            url: '/ajax/task/history',
            data: {
                'task_id' : task_id,
            },
            dataType: 'html',
            success: function (data) {
            if (data) {
                
                // console.log("Result:" + data);
                $('#task_history').html(data);
                
            } else {
                console.log("Error has occured during request");
            }

        }
        });
    
    }



     $("#btn_task_start").click(function () {
        task_id = $(this).attr('task-id')
        start_date = $('#start_date_val').val();
        if(! (start_date.length > 0 ) ) {
            alert('Please set the start date');
            return false;
        }
        
        console.log( ' starting task_id ' + task_id + ' from date ' + start_date );

        message_box = $('#message');
        $.ajax({
            url: '/ajax/task/start',
            data: {
                'task_id' : task_id,
                'start_date': start_date
            },
            dataType: 'json',
            success: function (data) {
            if (data.result) {
                console.log("Result:" + data.result);
                message_box.text(data.result);
                $('#start_date_block').html("Next scheduled date: <span id='next_date_val'>" + data.next_date_val + "</span>");

                
            } else {
                console.log("Error has occured during request");
                message_box.text('Error has occured during request');
            }
            message_box.fadeIn('slow', function(){
                message_box.delay(5000).fadeOut(); 
            });
            refreshHistory(task_id);

        }
        });
        return false;
    });
    

     $("#link_task_done").click(function () {
        task_id = $(this).attr('task-id')
        console.log( ' marking as done  task_id ' + task_id  );

        message_box = $('#message');
        $.ajax({
            url: '/ajax/task/done',
            data: {
                'task_id' : task_id
            },
            dataType: 'json',
            success: function (data) {
            if (data.result) {
                console.log("Result:" + data.result);
                message_box.text(data.result);
                $('#next_date_val').text(data.next_date_val);

                
            } else {
                console.log("Error has occured during request");
                message_box.text('Error has occured during request');
            }
            message_box.fadeIn('slow', function(){
                message_box.delay(5000).fadeOut(); 
            });
            refreshHistory(task_id);

        }
        });
        return false;
    });
    
     $(".link_task_postpone").click(function () {
        task_id = $(this).attr('task-id');
        delay_shift = $(this).attr('delay-shift');        
        console.log(' delaying task_id ' + task_id + ' for ' + delay_shift + ' days' );
        message_box = $('#message');
        $.ajax({
            url: '/ajax/task/postpone',
            data: {
                'task_id' : task_id,
                'delay_shift' : delay_shift
            },
            dataType: 'json',
            success: function (data) {
            if (data.result) {
                
                console.log("Result:" + data.result);
                message_box.text(data.result);
                $('#next_date_val').text(data.next_date_val);
                
            } else {
                console.log("Error has occured during request");
                message_box.text('Error has occured during request');
            }
            message_box.fadeIn('slow', function(){
                message_box.delay(5000).fadeOut(); 
            });
            refreshHistory(task_id);

        }
        });
        return false;
    });


});    
