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

// Función para filtrar tablas
function filterTable(tableId, inputId) {
    var input, filter, table, tr, td, i, j, txtValue;
    input = document.getElementById(inputId);
    filter = input.value.toUpperCase();
    table = document.getElementById(tableId);
    tr = table.getElementsByTagName("tr");

    for (i = 1; i < tr.length; i++) {
        tr[i].style.display = "none";
        td = tr[i].getElementsByTagName("td");
        for (j = 0; j < td.length; j++) {
            if (td[j]) {
                txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                    break;
                }
            }
        }
    }
}
