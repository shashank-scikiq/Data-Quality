$(function() {

    // var start = moment().subtract(29, 'days');
    // var end = moment();

    // function cb(start, end) {
    //     $('#filterDaterange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
    // }

    // $('#filterDaterange').daterangepicker({
    //   startDate: start,
    //   endDate: end,
    //   "opens": "left",
    //   "alwaysShowCalendars": true,
    //   ranges: {
    //       'Today': [moment(), moment()],
    //       'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
    //       'Last 7 Days': [moment().subtract(6, 'days'), moment()],
    //       'Last 30 Days': [moment().subtract(29, 'days'), moment()],
    //       'This Month': [moment().startOf('month'), moment().endOf('month')],
    //       'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
    //   }
    // }, cb);

    // cb(start, end);

});

$("#columnName").select2();
$("#sellerNps").select2();



var options = {
  chart: {
    type: "area",
    height: 280,
    foreColor: "#999",
    stacked: true,
    toolbar: {
        show: false
      },
    zoom: {
        enabled: false
      }
  
  },
  colors: ['#00E396', '#0090FF'],
  stroke: {
    curve: "smooth",
    width: 3
  },
  dataLabels: {
    enabled: false
  },
  series: [{
    name: 'Total Views',
    data: generateDayWiseTimeSeries(0, 18)
  }, {
    name: 'Unique Views',
    data: generateDayWiseTimeSeries(1, 18)
  }],
  markers: {
    size: 0,
    strokeColor: "#fff",
    strokeWidth: 3,
    strokeOpacity: 1,
    fillOpacity: 1,
    hover: {
      size: 6
    }
  },
  xaxis: {
    type: "datetime",
    axisBorder: {
      show: false
    },
    axisTicks: {
      show: false
    }
  },
  yaxis: {
    labels: {
      offsetX: 14,
      offsetY: -5
    },
    tooltip: {
      enabled: true
    }
  },
  grid: {
    padding: {
      left: -5,
      right: 5
    }
  },
  tooltip: {
    x: {
      format: "dd MMM yyyy"
    },
  },
  legend: {
    position: 'top',
    horizontalAlign: 'left'
  },
  fill: {
    type: "solid",
    fillOpacity: 0.7
  }
};

var chart = new ApexCharts(document.querySelector("#timeline-chart"), options);

chart.render();

function generateDayWiseTimeSeries(s, count) {
  var values = [[
    4,3,10,9,29,19,25,9,12,7,19,5,13,9,17,2,7,5
  ], [
    2,3,8,7,22,16,23,7,11,5,12,5,10,4,15,2,6,2
  ]];
  var i = 0;
  var series = [];
  var x = new Date("11 Nov 2012").getTime();
  while (i < count) {
    series.push([x, values[s][i]]);
    x += 86400000;
    i++;
  }
  return series;
}


var options2 = {
  chart: {
    height: 290,
    type: "area",
    stacked: true,
    toolbar: {
        show: false
      },
    zoom: {
        enabled: false
      }

  },
  colors: ["#008FFB", "#00E396", "#CED4DC"],
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: "smooth"
  },

  series: [
    {
      name: "South",
      data: generateDayWiseTimeSeries2(
        new Date("11 Feb 2017 GMT").getTime(),
        20,
        {
          min: 10,
          max: 60
        }
      )
    },
    {
      name: "North",
      data: generateDayWiseTimeSeries2(
        new Date("11 Feb 2017 GMT").getTime(),
        20,
        {
          min: 10,
          max: 20
        }
      )
    },

    {
      name: "Central",
      data: generateDayWiseTimeSeries2(
        new Date("11 Feb 2017 GMT").getTime(),
        20,
        {
          min: 10,
          max: 15
        }
      )
    }
  ],
  fill: {
    type: "gradient",
    gradient: {
      opacityFrom: 0.6,
      opacityTo: 0.8
    }
  },
  legend: {
    position: "top",
    horizontalAlign: "left"
  },
  xaxis: {
    type: "datetime"
  },
  tooltip: {
    custom: function({ series, seriesIndex, dataPointIndex, w }) {
      return `
            <div class="apexcharts-tooltip-custom">
              <strong>Total:</strong> ${
                w.globals.stackedSeriesTotals[dataPointIndex]
              }
            </div>`;
    }
  }
};

var chart = new ApexCharts(document.querySelector("#timeline-chart2"), options2);

chart.render();

function generateDayWiseTimeSeries2(baseval, count, yrange) {
  var i = 0;
  var series = [];
  while (i < count) {
    var x = baseval;
    var y =
      Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;

    series.push([x, y]);
    baseval += 86400000;
    i++;
  }
  return series;
}



// Sample data
var data = [
  { labels: 'Delivery City', series: 40.1 },
  { labels: 'Item Category', series: 2.3 },
  { labels: 'Category', series: 2.16 },
  { labels: 'Seller Pincode', series: 0.012 },
  { labels: 'Provider ID', series: 0.01 },
  { labels: 'Seller City', series: 2.16 }
  
];

var container = document.getElementById("missingValue");

data.forEach(function(entry, index) {
  var chartId = "radialChart" + index;

  var chartCardHTML = `
    <div class="card bg-light p-0">
      <div class="card-title tx-left pd-x-5 pd-t-5 m-0">${entry.labels}</div>
      <div class="card-body p-0">
        <div id="${chartId}" class="radial-chart-container"></div>
      </div>
    </div>
  `;

  var chartCard = document.createElement("div");
  chartCard.setAttribute("class", "radialchartcard w-100");
  chartCard.innerHTML = chartCardHTML;

  container.appendChild(chartCard);

  var options = {
    series: [entry.series],
    chart: {
      width: 130,
      type: 'radialBar'
    },
    plotOptions: {
      radialBar: {
        hollow: {
          margin: 0,
          size: '80%',
          background: '#fff',
          position: 'front',
        },
        track: {
          background: '#e5e9f2',
          // strokeWidth: '50px',
          margin: 0,
        },
        dataLabels: {
          show: true,
          name: {
            offsetY: 17,
            show: false,
            color: '#8392a5',
            fontSize: '11px'
          },
          value: {
            color: '#001737',
            fontSize: '12px',
            show: true,
            offsetY: 0,
          }
        }

      }

      
    },
    fill: {
      colors: ['#ff0000'] 
    },
    labels: [entry.labels]
  };

  var chart = new ApexCharts(chartCard.querySelector("#" + chartId), options);
  chart.render();
  
});

var options = {
    series: [76, 67],
    chart: {
    // width:180,
    // height: 60,
    type: 'radialBar',
  },
  plotOptions: {
    radialBar: {
      offsetX: 40,
      offsetY: -12,
      startAngle: 0,
      endAngle: 270,
      hollow: {
        margin: 10,
        size: '20%',
        background: 'transparent',
      },
      dataLabels: {
        name: {
          show: false,
          margin: 0,
        },
        value: {
          show: false,
          margin: 0,
        }
      },
      barLabels: {
        enabled: true,
        useSeriesColors: true,
        margin: 10,
        fontSize: '10px',
        formatter: function(seriesName, opts) {
          return seriesName + ":  " + opts.w.globals.series[opts.seriesIndex]
        },
      },
    }
  },
  colors: ['#ffc107', '#fd7e14'],
  labels: ['Today', 'Yesterday'],
  responsive: [{
    breakpoint: 480,
    options: {
      legend: {
          show: false
      }
    }
  }]
  };

  var chart = new ApexCharts(document.querySelector("#missingValchart"), options);
  chart.render();