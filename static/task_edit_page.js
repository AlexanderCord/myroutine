$(document).ready(function() {
 
   if(startDatepicker) {
     $('.datepicker').datepicker({
       dateFormat: 'yy-mm-dd',
       firstDay: 1,
     });
   }

   $('#id_period').on('change', function() {
     // custom period
     if(this.value == 2) {
        $('#id_period_data').parent().parent().show();
        $('#id_period_data').attr('required', 'required');
        $('#id_period_data').attr('min', '1');
        

        
     } else {
        $('#id_period_data').parent().parent().hide();
        $('#id_period_data').removeAttr('required');
        $('#id_period_data').removeAttr('min');
        
     }
   });
   $('#id_period').trigger('change');
   // @todo mobile-responsive custom style
   if($(window).width < 100) {
       $('#id_task').attr('style', 'width: 200px')

   } else {
       $('#id_task').attr('style', 'width: 400px')
   }
 });    
