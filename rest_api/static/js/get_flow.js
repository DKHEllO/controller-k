/**
 * Created by kd on 18-3-14.
 */
function draw_flow(name, description, y_name, x_name, div_id, data) {
    Highcharts.chart(div_id, {

        title: {
            text: name
        },

        subtitle: {
            text: description
        },
        xAxis: {
			type: 'datetime',
			dateTimeLabelFormats: { // don't display the dummy year
				month: '%e. %b',
				year: '%Y'
			},
			title: {
				text: x_name
			}
		},
        yAxis: {
            title: {
                text: y_name
            }
        },
        tooltip: {
			headerFormat: '<b>{series.name}</b><br>',
			pointFormat: '{point.x:%Y-%m-%d %H:%M:%S}<br>{point.y:.2f}' + y_name
		},
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle'
        },

        plotOptions: {
            series: {
                label: {
                    connectorAllowed: false
                }
            }
        },

        series: data,

        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom'
                    }
                }
            }]
        }

    });
}
