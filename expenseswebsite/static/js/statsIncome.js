const renderChart = (labels, data) => {
    var ctx = document.getElementById('myChartIncome').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Last 6 months expenses',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            title: {
                display: true,
                text: 'Incomes per categories'
            }
        }
    });
}

const getChartData = () => {
    fetch("income_source_summary/")
        .then((res) => res.json())
        .then((data) => {
            console.log("data", data);
            const results = data["income_source_data"];
            const [labels, datas] = [Object.keys(results), Object.values(results)];
            renderChart(labels, datas);
        })
};

document.onload = getChartData();