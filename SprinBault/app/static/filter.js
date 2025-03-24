function filterColumns() {
    let select = document.getElementById("columnFilter");
    let selectedColumn = select.value;
    let table = document.getElementById("dataTable");
    let ths = table.getElementsByTagName("th");
    let tds = table.getElementsByTagName("td");

    for (let i = 0; i < ths.length; i++) {
        let column = ths[i].getAttribute("data-column");
        let isVisible = selectedColumn === "all" || column === selectedColumn;

        ths[i].style.display = isVisible ? "" : "none";

        for (let j = i; j < tds.length; j += ths.length) {
            tds[j].style.display = isVisible ? "" : "none";
        }
    }
}

function filterByID() {
    let input = document.getElementById("idFilter").value.toLowerCase();
    let table = document.getElementById("dataTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) { // Empezamos en 1 para evitar la cabecera
        let cell = rows[i].getElementsByTagName("td")[0]; // ID está en la primera columna
        if (cell) {
            let textValue = cell.textContent || cell.innerText;
            rows[i].style.display = textValue.includes(input) ? "" : "none";
        }
    }
}