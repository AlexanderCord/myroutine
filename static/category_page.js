$(document).ready(function() {


     $(".link_remove_category").click(function () {
        if(!window.confirm("Do you really want to remove this category?")) {
            return false;
        }

        category_id = $(this).attr('category-id')
        category_row = $('#category_row_'+category_id);
        
        
        console.log( ' removing category ' + category_id );

        message_box = $('#message');
        $.ajax({
            url: '/ajax/category/remove',
            data: {
                'category_id' : category_id,
            },
            dataType: 'json',
            success: function (data) {
            if (data.result) {
                console.log("Result:" + data.result);
                message_box.text(data.result);
                category_row.remove();

            } else {
                console.log("Error has occured during request");
                message_box.text('Error has occured during request');
            }
            message_box.fadeIn('slow', function(){
                message_box.delay(5000).fadeOut(); 
            });

        }
        });
        return false;
    });
    



});    
