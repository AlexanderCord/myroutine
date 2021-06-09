$(document).ready(function() {
    function loadCharts() {


        $.ajax({
            url: '/ajax/task/stats',
            data: {},
            dataType: 'json',
            success: function(data) {
                console.log(data.result)
                if (data.result) {
                    let dataPoints = {'all' : [], 'yes' : [], 'no' : []};
                    let labelPoints = [];
                    tab = 'all'
                    for(let i=0; i < data.result['data_'+tab].length; i++){
                        let item = data.result['data_'+tab][i];
                        labelPoints[labelPoints.length] = moment(item._id).format("L")
                        
                    }
                    console.log('data points')
                    console.log(labelPoints);
                    tempData = {'all' : {}, 'yes' : {}, 'no' : {}};
                    ['all', 'yes', 'no'].forEach(tab => {
                        
                        
                        for(let i=0; i < data.result['data_'+tab].length; i++){
                            let item = data.result['data_'+tab][i];
                            itemDate = moment(item._id).format("L");
                            tempData[tab][ itemDate ] = item.count;                                                                        
                        }
                        
                            
                        
                    });
                    console.log('temp data')
                    console.log(tempData);
                    ['all', 'yes', 'no'].forEach(tab => {
                        for(let j = 0; j< labelPoints.length; j++) {
                            currentDate = labelPoints[j];
                            dataPoints[tab][dataPoints[tab].length] = 
                            {
                                x: currentDate,
                                y: tempData[tab][currentDate] ? tempData[tab][currentDate] : 0
                            }
                        }
                    });
                    console.log('data points');
                    console.log(dataPoints);

                    var config = {
                        type: 'line',
                        data: {
                            labels: labelPoints,
                            datasets: [{
                                label: 'Task stats (last 30 days)',
                                backgroundColor: '#000000',
                                borderColor: '#000000',
                                data: dataPoints['all'],
                                fill: false,
                            }, {
                                label: 'Done',
                                backgroundColor: '#28a745',
                                borderColor: '#28a745',
                                data: dataPoints['yes'],
                                fill: false,
                            }, {
                                label: 'Postponed',
                                backgroundColor: '#dc3545',
                                borderColor: '#dc3545',
                                data: dataPoints['no'],
                                fill: false,
                            }, ]
                        },


                        options: {
                            responsive: true,
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Task stats (last 30 days)'
                                },
                                tooltip: {
                                    mode: 'index',
                                    intersect: false,
                                }
                            },
                            hover: {
                                mode: 'nearest',
                                intersect: false
                            },
                            scales: {
                                x: {
                                    display: true,
                                    scaleLabel: {
                                        display: true,
                                        labelString: 'Date',
                                        type: 'time',
                                        time: {
                                            parser: 'MM/DD/YYYY',
                                            // round: 'day'
                                            tooltipFormat: 'DD MMMM YYYY'
                                        },

                                    }
                                },
                                y: {
                                    display: true,
                                    scaleLabel: {
                                        display: true,
                                        labelString: 'Value'
                                    }
                                }
                            }
                        }
                    };
                    var ctx = document.getElementById('statsCanvas').getContext('2d');
			        window.myLine = new Chart(ctx, config);

                }   

            }
        });

        
    }
    loadCharts();
});

