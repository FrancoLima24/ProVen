document.addEventListener('DOMContentLoaded', function () {
    var accordionButtons = document.querySelectorAll('.accordion-button');
    accordionButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            var content = this.nextElementSibling;
            var searchInput = content.querySelector('input[type="text"]');

            // Expand or collapse the content
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                searchInput.style.display = 'none';  // Ocultar el buscador al colapsar
            } else {
                content.classList.add('active');
                searchInput.style.display = 'block'; // Mostrar el buscador al expandir
            }
        });
    });
});

// Función para ordenar las tablas
function sortTable(columnIndex, tableClass) {
    var table = document.getElementsByClassName(tableClass)[0];
    var rows = table.rows;
    var switching = true;
    var shouldSwitch;
    var i;
    var direction = "asc"; 
    var switchCount = 0;

    while (switching) {
        switching = false;
        var rowsArray = Array.from(rows).slice(1);

        for (i = 0; i < rowsArray.length - 1; i++) {
            shouldSwitch = false;
            var x = rowsArray[i].getElementsByTagName("TD")[columnIndex];
            var y = rowsArray[i + 1].getElementsByTagName("TD")[columnIndex];

            if (direction === "asc" && x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                shouldSwitch = true;
                break;
            } else if (direction === "desc" && x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                shouldSwitch = true;
                break;
            }
        }

        if (shouldSwitch) {
            rowsArray[i].parentNode.insertBefore(rowsArray[i + 1], rowsArray[i]);
            switching = true;
            switchCount++;
        } else if (switchCount === 0 && direction === "asc") {
            direction = "desc";
            switching = true;
        }
    }
}

// Función para filtrar los datos de la tabla
function filterTable(inputId, tableClass) {
    var input = document.getElementById(inputId);
    var filter = input.value.toLowerCase();
    var table = document.getElementsByClassName(tableClass)[0];
    var rows = table.getElementsByTagName("tr");

    for (var i = 1; i < rows.length; i++) {
        var row = rows[i];
        var rowData = row.innerText.toLowerCase();
        row.style.display = rowData.indexOf(filter) > -1 ? "" : "none";
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
    const sidebar = document.getElementById('sidebar');
    const mainContainer = document.querySelector('.main-container');

    toggleSidebarBtn.addEventListener('click', function () {
        // Cambiar la clase 'active' de la barra lateral
        sidebar.classList.toggle('active');

        // Ajustar el contenedor principal para dar espacio a la barra lateral
        if (sidebar.classList.contains('active')) {
            mainContainer.style.marginLeft = '200px';
        } else {
            mainContainer.style.marginLeft = '0';
        }
    });
});
