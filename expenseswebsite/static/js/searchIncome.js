const searchField = document.querySelector('#searchInput');
const tableOutput = document.querySelector('.table-output');
const appTable = document.querySelector('.app-table');
const paginationContainer = document.querySelector('.pagination-container');
const tableBody = document.querySelector('.table-body');
const noResults = document.querySelector('.no-results');
tableOutput.style.display = 'none';
noResults.style.display = 'none';
searchField.addEventListener('keyup', (e) => {

    const searchValue = e.target.value
    console.log(searchValue)
    tableBody.innerHTML = "";
    if (searchValue.trim().length > 0) {
        paginationContainer.style.display = 'none';
        fetch("/income/search-income/", {
                body: JSON.stringify({ searchText: searchValue }),
                method: "POST",
            })
            .then((res) => res.json())
            .then((data) => {
                console.log("data", data);
                tableOutput.style.display = 'block';
                appTable.style.display = 'none';
                if (data.length == 0) {
                    console.log("No data")
                    noResults.style.display = "block";
                    tableOutput.style.display = 'none';
                } else {
                    data.forEach((items) => {
                        console.log("have data")
                        noResults.style.display = "none";
                        tableBody.innerHTML += `
                        <tr>
                            <td>${ items.amount }</td>
                            <td>${ items.source }</td>
                            <td>${ items.description }</td>
                            <td>${ items.date }</td>
                        </tr>`;
                    });
                }
            });

    } else {

        appTable.style.display = 'block';
        paginationContainer.style.display = 'block';
        tableOutput.style.display = 'none';
    }
});