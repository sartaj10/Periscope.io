$(function () {
    $('#container').highcharts({
        chart: {
            type: 'bar'
        },
        title: {
            text: 'World\'s largest cities per 2014'
        },
        xAxis: {
            type: 'linear',
            title: {
                text: 'Value'
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Amount'
            }
        },
        legend: {
            enabled: false
        },
        series: [{
            name: 'Amount',
            data: {{ name[0]|safe }}
        }]
    });
});