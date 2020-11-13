$(document).ready(function() {


    function getTotalTaskCount() {
        var sum = 0;
        $('.task_category_count').each(function(){
            sum += parseInt($(this).text());  
        });
        
        $('#total_task_count').text("(" + sum + ")");
    }
    
    getTotalTaskCount();


});    
