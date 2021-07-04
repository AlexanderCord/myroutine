$(document).ready(function() {


    function getTotalTaskCount() {
        var sum = 0;
        $('.task_category_count').each(function(){
            sum += parseInt($(this).text());  
        });
        
        $('#total_task_count').text("(" + sum + ")");
    }
    getTotalTaskCount();
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



});    
